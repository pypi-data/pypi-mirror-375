"""
DROK XY-T01 digital temperature controller — UART driver (async reader + acks)

This module provides a thin, threadsafe UART driver for the XY-T01 controller
(using `pyserial`). It supports safe start/stop sequencing, and a background reader
thread that demultiplexes asynchronous measurements from command responses.

Protocol summary (observed/empirical):

- **Serial**: default ``/dev/serial1``, ``9600 8N1``, text mode lines ending with LF (``"\n"``)
- **Commands** (lowercase **except** uppercase **S** for setpoint):

  * **setpoint**: ``S:XXX``

    - Range: ``-50..110 °C``. Encodings: ``-NN`` for negatives; tenths w/o dot and
      trimming redundant zero for ``0..99.9``; three digits ``NNN`` for ``100..110``.

  * **alarm**: ``ALA:XXX``

    - Range/encoding similar to setpoint, but ``0..99.9`` is ``XX.X`` (one decimal).
    - Ack payload is **state**: ``DOWN`` or ``UP``.

  * **power**: ``on`` / ``off`` (ack: ``DOWN``)
  * **stream**: ``start`` / ``stop`` (ack: ``DOWN``)
  * **read**: ``read``, three lines in order:

    1. ``H,88.0,02.0``  (``H`` or ``C`` = heat/cool mode, setpoint °C, hysteresis °C)
    2. ``ALA:60.0,OPH:0000,OFE:0.00``  (alarm °C, start-delay minutes, calibration °C)
    3. ``DOWN`` | ``UP`` (current relay/output state)

- **NACK**: ``FAIL`` for unknown/invalid command
- **Measurements** (asynchronous lines): ``<temp>,<mode>`` (e.g., ``57.0,CL``) where
  modes are ``CL`` (cool), ``OP`` (heat), or ``OFF`` (disabled)

The reader thread continuously consumes lines. If a line is recognized as an
asynchronous measurement, the configured callback is invoked. Otherwise the line
is routed to the current command waiter (single in-flight command constraint).

Example
-------

.. code-block:: python

    from drok_xyt01_driver_sphinxified import DrokXYT01, DrokXYT01Config

    with DrokXYT01(DrokXYT01Config()) as ctl:
        if not ctl.connect(on_measurement=lambda mode, t: print(mode, t)):
            print("Failed to connect")
            return
        print(ctl.query_state())
        ctl.set_setpoint(45.0)
        ctl.on()

Notes
-----
- Ack waits time out after ``ack_timeout_s`` (default 3 s).
- The class is a context manager to ensure timely shutdown of the reader thread
  and the serial port.
"""

# SPDX-FileCopyrightText: (c) 2025 Jeff C. Jensen
# SPDX-License-Identifier: MIT

from __future__ import annotations

import contextlib
import logging
import queue
import threading
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any

import serial  # pyserial

__all__ = [
    "DrokXYT01",
    "DrokXYT01Config",
    "DrokXYT01State",
]


# =============================
# Configuration & State Models
# =============================


@dataclass
class DrokXYT01Config:
    """Serial and timing configuration for :class:`DrokXYT01`.

    :param port: Serial device path.
    :param baudrate: UART baud rate.
    :param read_timeout_s: Serial ``readline`` timeout (seconds).
    :param write_timeout_s: Serial write timeout (seconds).
    :param crlf: Line terminator appended to transmitted commands.
    :param ack_timeout_s: Maximum time to wait for a command's response lines.
    :param txrx_delay_s: Inter-command delay between TX and the first RX wait.
    """

    port: str = "/dev/serial1"
    baudrate: int = 9600
    read_timeout_s: float = 2.0
    write_timeout_s: float = 1.0
    crlf: str = "\n"
    ack_timeout_s: float = 3.0
    txrx_delay_s: float = 1.0


@dataclass
class DrokXYT01State:
    """Structured state returned by :meth:`DrokXYT01.query_state`.

    :ivar mode: ``"heat"`` or ``"cool"`` (derived from H/C), or ``None`` if unknown.
    :ivar setpoint_c: Setpoint temperature in °C, if available.
    :ivar hysteresis_c: Hysteresis in °C, if available.
    :ivar alarm_c: Alarm threshold in °C, if available.
    :ivar start_delay_min: Output start delay (``OPH``) in minutes, if available.
    :ivar calibration_bias_c: Calibration offset (``OFE``) in °C, if available.
    """

    mode: str | None
    setpoint_c: float | None
    hysteresis_c: float | None
    alarm_c: float | None
    start_delay_min: int | None
    calibration_bias_c: float | None


# =============================
# Internal utilities
# =============================


class _Waiter:
    """Waiter state for a single in-flight command.

    :param expect_lines: Number of response lines expected for the command.
    """

    def __init__(self, expect_lines: int):
        self.expect_lines = expect_lines
        self.q: queue.Queue[str] = queue.Queue()


# =============================
# Driver
# =============================


class DrokXYT01:
    """XY-T01 controller driver with asynchronous reader and synchronous acks.

    This class manages the serial port, a background reader thread that
    demultiplexes measurements and command responses, and a simple command API.

    Thread safety: one command may be in flight at a time. A dedicated TX lock
    serializes writes. The reader thread safely hands response lines to the
    active waiter, if any.

    :param config: Serial and timing configuration.
    """

    def __init__(self, config: DrokXYT01Config):
        self.config = config
        self._device: serial.Serial | None = None
        self._reader_thread: threading.Thread | None = None
        self._stop_evt = threading.Event()
        self._tx_lock = threading.Lock()
        self._on_measurement: Callable[[str, float], None] | None = None
        self._waiter_lock = threading.Lock()
        self._waiter: _Waiter | None = None
        self.log = logging.getLogger(self.__class__.__name__)

    # ------------- Lifecycle -------------
    def __enter__(self) -> DrokXYT01:
        """Enter context manager and return ``self``.

        The serial port is not opened automatically here to avoid side effects.
        Call :meth:`connect` explicitly, or use the pattern::

            with DrokXYT01(cfg) as ctl:
                ctl.connect(...)
        """

        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        """Ensure :meth:`disconnect` is called on context exit."""

        try:
            self.disconnect()
        except Exception:  # pragma: no cover — best effort cleanup
            self.log.exception("Cleanup during __exit__ failed")

    @property
    def is_connected(self) -> bool:
        """Whether the serial port is open.

        :return: ``True`` if the serial device is open.
        """

        return bool(self._device and self._device.is_open)

    def connect(self, on_measurement: Callable[[str, float], None] | None = None) -> bool:
        """Open the serial port and start the reader thread.

        A safe configuration sequence is issued: ``stop``, ``off``, short delay,
        ``start`` to enable streaming. This is the safe-state sequence.

        :param on_measurement: Optional callback ``(mode: str, temp_c: float)`` that
            receives asynchronous measurement updates. ``mode`` is one of
            ``{"CL", "OP", "OFF"}``. Must return quickly or risk blocking additional reads.
        :return: ``True`` if connected and reader started; otherwise ``False``.
        """

        if self.is_connected:
            return True

        self._on_measurement = on_measurement
        try:
            self._device = serial.Serial(
                port=self.config.port,
                baudrate=self.config.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=self.config.read_timeout_s,
                write_timeout=self.config.write_timeout_s,
                xonxoff=False,
                rtscts=False,
                dsrdtr=False,
            )
        except Exception as e:  # pragma: no cover — hardware dependent
            self.log.error("Failed to open serial port %s: %s", self.config.port, e)
            self._device = None
            return False

        self.log.info("Opened %s @ %d 8N1 (EOL=LF)", self.config.port, self.config.baudrate)
        self._clear_buffers()

        # Reader thread (handles both stream + command responses)
        self._stop_evt.clear()
        try:
            self._reader_thread = threading.Thread(
                target=self._reader_loop, name="xyt01-rx " + self.config.port, daemon=False
            )
            self._reader_thread.start()
        except Exception as e:
            self.log.error("Failed to start reader thread: %s", e)
            with contextlib.suppress(Exception):
                self._device and self._device.close()
            self._device = None
            return False

        # Safe state & configuration sequence (all expect ack 'DOWN')
        self.stop()
        self.off()
        time.sleep(0.05)
        self.start()  # start streaming
        return True

    def disconnect(self) -> None:
        """Stop the reader, close the serial port, and leave the controller OFF."""

        # Best effort to put device in a safe state
        try:
            if self.is_connected:
                self.off()
        except Exception:
            pass
        try:
            if self.is_connected:
                self.stop()
        except Exception:
            pass

        # Stop reader thread
        self._stop_evt.set()
        if self._reader_thread and self._reader_thread.is_alive():
            self._reader_thread.join(timeout=self.config.read_timeout_s + 1.0)
        self._reader_thread = None

        # Close port
        if self._device:
            try:
                self._clear_buffers()
                self._device.close()
            except Exception as e:
                self.log.warning("Error while closing port: %s", e)
            finally:
                self._device = None

    # ------------- High-level commands (ack via reader) -------------
    def start(self) -> bool:
        """Start streaming measurements.

        :return: ``True`` on expected ack, else ``False``.
        """

        return self._send_and_wait_ack("start", expect_lines=1, expect_states={"DOWN"})

    def stop(self) -> bool:
        """Stop streaming measurements.

        :return: ``True`` on expected ack, else ``False``.
        """

        return self._send_and_wait_ack("stop", expect_lines=1, expect_states={"DOWN"})

    def on(self) -> bool:
        """Turn controller output **ON**.

        :return: ``True`` on expected ack, else ``False``.
        """

        return self._send_and_wait_ack("on", expect_lines=1, expect_states={"DOWN"})

    def off(self) -> bool:
        """Turn controller output **OFF**.

        :return: ``True`` on expected ack, else ``False``.
        """

        return self._send_and_wait_ack("off", expect_lines=1, expect_states={"DOWN"})

    def set_setpoint(self, temp_c: float) -> bool:
        """Set the controller setpoint.

        :param temp_c: Setpoint in °C (``-50..110``).
        :return: ``True`` on expected ack, else ``False``.
        """

        payload = self._fmt_setpoint(temp_c)
        if payload is None:
            return False
        return self._send_and_wait_ack(f"S:{payload}", expect_lines=1, expect_states={"DOWN"})

    def set_alarm(self, temp_c: float) -> bool:
        """Set the controller alarm threshold.

        :param temp_c: Alarm in °C (``-50..110``).
        :return: ``True`` if an expected state (``DOWN`` or ``UP``) is received.
        """

        payload = self._fmt_alarm(temp_c)
        if payload is None:
            return False
        return self._send_and_wait_ack(
            f"ALA:{payload}", expect_lines=1, expect_states={"DOWN", "UP"}
        )

    def read_settings(self) -> tuple[str, str, str]:
        """Read the three settings/state lines from the controller.

        :return: Tuple of three raw lines (L1, L2, L3). Empty strings on timeout.
        """
        lines = self._send_and_wait_lines("read", expect_lines=3)
        if len(lines) != 3:
            self.log.warning("read: expected 3 lines, got %d: %s", len(lines), lines)

        # Pad to length 3
        l1 = lines[0] if len(lines) > 0 else ""
        l2 = lines[1] if len(lines) > 1 else ""
        l3 = lines[2] if len(lines) > 2 else ""
        return (l1, l2, l3)

    def query_state(self) -> DrokXYT01State:
        """Return structured device state.

        This issues a ``read`` and parses the result into a :class:`DrokXYT01State`.

        :return: Parsed :class:`DrokXYT01State`.
        """

        lines = self.read_settings()
        return DrokXYT01._parse_read_lines_to_state(lines)

    def reset(self) -> None:
        """Reset the controller and reconnect.

        The sequence is: ``stop``, ``off``, wait ~2 s, clear buffers, disconnect, connect.
        The existing measurement callback is preserved.
        """

        try:
            self.stop()
            self.off()
        except Exception:
            pass
        time.sleep(2.0)
        self._clear_buffers()
        self.disconnect()
        self.connect(on_measurement=self._on_measurement)

    def enable_logging(self, verbose: bool = False) -> None:
        """Configure module logging with a simple formatter.

        :param verbose: If ``True``, use ``DEBUG`` level; otherwise ``INFO``.
        """

        logging.basicConfig(
            level=logging.DEBUG if verbose else logging.INFO,
            format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        )

    # ------------- Internals -------------
    def _send_and_wait_ack(self, cmd: str, expect_lines: int, expect_states: set[str]) -> bool:
        """Send a command and wait for expected ack state(s).

        :param cmd: Command text (without terminator).
        :param expect_lines: Number of response lines to collect.
        :param expect_states: Set of acceptable final ack tokens (e.g., ``{"DOWN"}``).
        :return: ``True`` if any collected line matches an expected state; else ``False``.
        """

        lines = self._send_and_wait_lines(cmd, expect_lines=expect_lines)
        ok = False
        for resp in lines:
            r = resp.strip().upper()
            if r == "FAIL":
                self.log.warning("%s: device responded FAIL", cmd)
            if r in expect_states:
                ok = True
        if not ok and lines:
            self.log.warning("%s: unexpected response(s): %s", cmd, lines)
        return ok

    def _send_and_wait_lines(self, cmd: str, expect_lines: int) -> list[str]:
        """Send a command and wait for up to ``expect_lines`` response lines.

        :param cmd: Command text (without terminator).
        :param expect_lines: Number of lines to gather before returning.
        :return: List of collected lines (may be shorter on timeout or error).
        """

        if not self.is_connected:
            self.log.error("Serial port not open")
            return []

        # Install waiter
        with self._waiter_lock:
            if self._waiter is not None:
                self.log.error("Another command is in flight")
                return []
            self._waiter = _Waiter(expect_lines)

        # Transmit
        line = (cmd + self.config.crlf).encode("ascii")
        try:
            with self._tx_lock:
                self.log.debug("TX: %s", cmd)
                self._device.write(line)  # type: ignore[union-attr]
                self._device.flush()  # type: ignore[union-attr]
        except Exception as e:
            self.log.error("TX error for '%s': %s", cmd, e)
            with self._waiter_lock:
                self._waiter = None
            return []

        # Delay before waiting (empirically helps)
        time.sleep(self.config.txrx_delay_s)

        # Wait for N lines or timeout
        got: list[str] = []
        deadline = time.time() + self.config.ack_timeout_s
        try:
            while len(got) < expect_lines:
                remaining = max(0.0, deadline - time.time())
                if remaining == 0:
                    break
                try:
                    s = self._waiter.q.get(timeout=remaining)
                    got.append(s)
                except queue.Empty:
                    break
        finally:
            with self._waiter_lock:
                self._waiter = None

        if len(got) < expect_lines:
            self.log.warning(
                "%s: timed out waiting for %d line(s); got %d: %s",
                cmd,
                expect_lines,
                len(got),
                got,
            )
        return got

    def _reader_loop(self) -> None:
        """Continuously read lines, dispatching to measurement callback or waiter.

        Lines are decoded as ASCII, ``errors='ignore'``. Unsolicited lines without
        a current waiter are logged at DEBUG level.
        """

        self.log.info("Reader thread started (timeout=%.1fs)", self.config.read_timeout_s)
        try:
            if self._device:
                self._device.timeout = self.config.read_timeout_s
        except Exception:
            pass

        while not self._stop_evt.is_set():
            try:
                if not self._device:
                    self.log.warning("Reader thread active after device left scope.")
                    break
                raw = self._device.readline()
                if not raw:
                    continue
                s = raw.decode("ascii", errors="ignore").strip()
                if not s:
                    continue
                self.log.debug("RX: %s", s)

                # Measurement vs response classification
                t_c, mode = self._try_parse_measurement(s)
                if t_c is not None and mode is not None:
                    if self._on_measurement:
                        try:
                            self._on_measurement(mode, t_c)
                        except Exception:
                            self.log.exception("on_measurement callback error")
                    continue  # consumed by measurement path

                # Otherwise, deliver to any waiting command
                delivered = False
                with self._waiter_lock:
                    if self._waiter is not None:
                        self._waiter.q.put(s)
                        delivered = True
                if not delivered:
                    self.log.debug("unsolicited: %s", s)

            except Exception as e:
                self.log.warning("reader error: %s", e)

        self.log.info("Reader thread stopped")

    @staticmethod
    def _parse_read_lines_to_state(lines: Sequence[str]) -> DrokXYT01State:
        """Parse the three lines returned by ``read`` into a :class:`DrokXYT01State`.

        :param lines: Iterable of at least two lines; the function uses up to three.
        :return: Parsed :class:`DrokXYT01State` with ``None`` for any missing field.
        """

        logger = logging.getLogger("DrokXYT01")

        mode_hc: str | None = None
        setpoint_c: float | None = None
        hysteresis_c: float | None = None
        alarm_c: float | None = None
        start_delay_min: int | None = None
        calibration_bias_c: float | None = None

        # line 1: H/C, setpoint, hysteresis
        try:
            l1 = str(lines[0])
            p = [t.strip() for t in l1.split(",")]
            if len(p) >= 3:
                mode_hc = "heat" if p[0].upper().startswith("H") else "cool"
                setpoint_c = float(p[1])
                hysteresis_c = float(p[2])
            else:
                logger.warning("insufficient tokens in line 1: %r", l1)
        except Exception as e:
            logger.warning("malformed line 1: %r (%s)", lines[0] if lines else None, e)

        # line 2: ALA...,OPH...,OFE... OR DOWN
        l2 = (str(lines[1]) if len(lines) > 1 else "").strip()
        if l2.upper() != "DOWN":
            try:
                kv: dict[str, str] = {}
                for tok in l2.split(","):
                    if ":" in tok:
                        k, v = tok.split(":", 1)
                        kv[k.strip().upper()] = v.strip()
                alarm_c = float(kv["ALA"]) if "ALA" in kv else None
                start_delay_min = int(kv["OPH"]) if "OPH" in kv else None
                calibration_bias_c = float(kv["OFE"]) if "OFE" in kv else None
            except Exception as e:
                logger.warning("malformed line 2: %r (%s)", l2, e)

        return DrokXYT01State(
            mode_hc, setpoint_c, hysteresis_c, alarm_c, start_delay_min, calibration_bias_c
        )

    @staticmethod
    def _try_parse_measurement(s: str) -> tuple[float | None, str | None]:
        """Try to parse a measurement line of the form ``"<temp>,<mode>"``.

        :param s: Raw line (ASCII string without trailing LF).
        :return: ``(temp_c, mode)`` if recognized, otherwise ``(None, None)``.
        """

        if "," not in s:
            return None, None
        first, second = (t.strip() for t in s.split(",", 1))
        mode = second.upper()
        if mode not in {"CL", "OP", "OFF"}:
            return None, None
        try:
            return float(first), mode
        except Exception:
            return None, None

    def _clear_buffers(self) -> None:
        """Clear serial input/output buffers if the device is open."""

        if not self._device:
            return
        try:
            self._device.reset_input_buffer()
            self._device.reset_output_buffer()
        except Exception:
            pass

    # ----- format helpers -----
    @staticmethod
    def _fmt_setpoint(v: float) -> str | None:
        """Format a setpoint as required by the controller.

        Encoding rules:

        - ``[-50..-1]``: ``-NN``
        - ``[0..99.9]``: tenths without dot (drop trailing zero)
        - ``[100..110]``: ``NNN``

        :param v: Setpoint in °C.
        :return: Encoded string.
        """

        if v < -50 or v > 110:
            logging.getLogger("DrokXYT01").warning("Setpoint out of range (-50..110 °C): %s", v)
            return None
        if v < 0:
            n = round(v)
            n = max(-50, min(-1, n))
            return f"-{abs(n):02d}"
        if v < 100:
            vv = max(0.0, min(99.9, round(v, 1)))
            tenths = round(vv * 10)
            return str(tenths // 10) if tenths % 10 == 0 else str(tenths)
        n = round(v)
        n = max(100, min(110, n))
        return f"{n:03d}"

    @staticmethod
    def _fmt_alarm(v: float) -> str | None:
        """Format an alarm threshold as required by the controller.

        Encoding rules:

        - ``[-50..-1]``: ``-NN``
        - ``[0..99.9]``: ``XX.X`` (one decimal place)
        - ``[100..110]``: ``NNN``

        :param v: Alarm in °C.
        :return: Encoded string.
        """

        if v < -50 or v > 110:
            logging.getLogger("DrokXYT01").warning("Alarm out of range (-50..110 °C): %s", v)
            return None
        if v < 0:
            n = round(v)
            n = max(-50, min(-1, n))
            return f"-{abs(n):02d}"
        if v < 100:
            vv = max(0.0, min(99.9, round(v, 1)))
            return f"{vv:04.1f}"
        n = round(v)
        n = max(100, min(110, n))
        return f"{n:03d}"
