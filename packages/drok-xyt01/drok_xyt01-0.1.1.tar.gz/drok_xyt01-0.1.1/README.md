# DROK XY-T01 Driver

Thread-safe Python driver for the DROK XY-T01 digital temperature controller over UART.

Supports safe lifecycle sequencing, synchronous command API, and a background reader thread
that demultiplexes asynchronous measurement lines from command responses.

## Features

- Pure Python 3.12
- Async measurement reader + synchronous ACK handling
- Thread-safe single-command model
- Context-manager lifecycle
- Structured state parsing
- CLI for manual interaction
- Type-hinted & documented

## Installation

```shell
pip install drok-xyt01
```

## Quickstart

```python
from drok_xyt01 import DrokXYT01, DrokXYT01Config

def on_measurement(mode: str, temp_c: float) -> None:
    print(f"{mode} {temp_c:.1f} °C")

cfg = DrokXYT01Config(port="/dev/serial1")

with DrokXYT01(cfg) as ctl:
    if not ctl.connect(on_measurement=on_measurement):
        raise RuntimeError("Failed to connect")
    print("state:", ctl.query_state())
    ctl.set_setpoint(45.0)
    ctl.on()
```

## CLI

```shell
drok-xyt01 --port /dev/serial1 --verbose
```

## API Overview

- `connect(on_measurement=...)`: open port + start background reader
- `disconnect()`: stop thread + close port
- `start()` / `stop()`: start/stop measurement streaming
- `on()` / `off()`: control output relay
- `set_setpoint(temp_c)` / `set_alarm(temp_c)`: temperature setpoints
- `query_state()`: query device state
- `reset()`: safe reconnect sequence

## Resources

- Source code on Github: [elgeeko1/drok-xyt01](https://github.com/elgeeko1/drok-xyt01)
- API documentation: <https://elgeeko1.github.io/drok-xyt01/>
