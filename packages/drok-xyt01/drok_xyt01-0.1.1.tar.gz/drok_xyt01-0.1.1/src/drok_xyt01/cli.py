# SPDX-FileCopyrightText: (c) 2025 Jeff C. Jensen
# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import contextlib
import logging
import time

from .driver import DrokXYT01, DrokXYT01Config

__all__ = [
    "DrokXYT01Cli",
]


def DrokXYT01Cli() -> None:
    """Simple CLI for manual interaction and demonstration."""

    parser = argparse.ArgumentParser(description="DROK XY-T01 UART controller")
    parser.add_argument("--port", default="/dev/serial1")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    ctl = DrokXYT01(DrokXYT01Config(port=args.port))

    try:
        if not ctl.connect(on_measurement=lambda mode, t_c: print(f"{mode} {t_c:.1f} °C")):
            print("Failed to connect")
            return
        state = ctl.query_state()
        print("state:", state)
        ctl.set_setpoint(45.0)
        ctl.on()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        with contextlib.suppress(Exception):
            ctl.off()
        ctl.disconnect()


if __name__ == "__main__":
    DrokXYT01Cli()
