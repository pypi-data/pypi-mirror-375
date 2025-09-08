# Severstar MFC RS485 Control

![PyPI version](https://img.shields.io/pypi/v/severstar-mfc-rs485.svg)
![Python versions](https://img.shields.io/pypi/pyversions/severstar-mfc-rs485.svg)
![License](https://img.shields.io/pypi/l/severstar-mfc-rs485.svg)

A comprehensive Python package for RS485 communication with Severstar CS series digital mass flow controllers (MFCs) from Beijing Sevenstar Flow Co., Ltd.

## Features

- **Full Protocol Support**: Complete implementation of CS系列MFC通讯协议V2.3
- **High-level API**: Easy-to-use interface for common MFC operations
- **CLI Tool**: Command-line interface for device management and monitoring
- **Comprehensive Error Handling**: Robust exception hierarchy for reliable operation
- **Type Annotations**: Full type support for better development experience
- **Cross-platform**: Works on Windows, Linux, and macOS

## Supported Devices

- CS100 series digital mass flow controllers
- CS200 series digital mass flow controllers
- Other CS series devices with RS485 interface

## Installation

```bash
pip install severstar-mfc-rs485
```

## Quick Start

### Python API

```python
from severstar_mfc_rs485 import SeverstarMFC, discover_mfc_devices

# Discover devices
devices = discover_mfc_devices('/dev/ttyUSB0')
print(f"Discovered devices: {devices}")

# Connect to device
with SeverstarMFC('/dev/ttyUSB0', address=32) as mfc:
    # Get device information
    info = mfc.get_device_info()
    print(f"Serial: {info['serial_number']}")
    
    # Monitor flow rate
    flow_rate = mfc.get_flow_rate()
    print(f"Current flow: {flow_rate:.4f} FS")
    
    # Set flow to 50%
    mfc.set_flow_rate(0.5)
```

### Command Line Interface

```bash
# Discover devices
severstar_mfc_rs485 discover /dev/ttyUSB0

# Get device info
severstar_mfc_rs485 info /dev/ttyUSB0 --address 32

# Monitor status
severstar_mfc_rs485 status /dev/ttyUSB0 --address 32

# Set flow rate
severstar_mfc_rs485 set-flow /dev/ttyUSB0 0.5 --address 32
```

## Documentation

- **[Usage Guide](docs/usage.md)**: Comprehensive usage examples and API reference
- **[Protocol Reference](docs/protocol-reference.md)**: Detailed protocol specification
- **[Installation Guide](docs/installation.md)**: Setup and installation instructions

## Protocol Support

The package implements the complete CS series MFC communication protocol including:

- **Control Mode**: Closed loop, open loop, manual valve control
- **Flow Control**: Setpoint reading/writing, flow rate monitoring
- **Valve Control**: Valve output reading/writing
- **Calibration**: Full scale flow, zero flow, gas conversion factors
- **Temperature Monitoring**: Sensor and environment temperature
- **Totalizer**: Accumulated flow and operating time
- **Alarms**: Status and configuration
- **Device Identification**: Serial number, model, firmware version
- **Communication Settings**: MAC address, baud rate configuration

## API Overview

### Main Classes

- `SeverstarMFC`: High-level device interface
- `MFCCommunicator`: Low-level RS485 communication
- `MFCCommands`: Command-level operations
- `ProtocolMessage`: Protocol message encoding/decoding

### Data Types

- `ServiceType`: Read/Write service types
- `CommandClass`: Protocol command classes
- `ControlMode`: Control mode enumerations
- `DataFormat`: Data conversion utilities

## Examples

### Basic Monitoring

```python
import time
from severstar_mfc_rs485 import SeverstarMFC

def monitor_device(port, address):
    with SeverstarMFC(port, address) as mfc:
        while True:
            status = mfc.get_status()
            print(f"Flow: {status['flow_rate']:.4f} FS | "
                  f"Temp: {status['sensor_temperature']:.1f}°C")
            time.sleep(1)

monitor_device('/dev/ttyUSB0', 32)
```

### Flow Profile Control

```python
from severstar_mfc_rs485 import SeverstarMFC
import time

profile = [
    (0.0, 2.0),   # 0% for 2s
    (0.5, 5.0),   # 50% for 5s
    (0.8, 3.0),   # 80% for 3s
    (0.0, 1.0)    # 0% for 1s
]

with SeverstarMFC('/dev/ttyUSB0', 32) as mfc:
    for flow, duration in profile:
        mfc.set_flow_rate(flow)
        time.sleep(duration)
```

## Error Handling

```python
from severstar_mfc_rs485 import (
    CommunicationError, TimeoutError, InvalidParameterError
)

try:
    with SeverstarMFC('/dev/ttyUSB0', 32) as mfc:
        mfc.set_flow_rate(2.0)  # Invalid value
except InvalidParameterError as e:
    print(f"Invalid parameter: {e}")
except CommunicationError as e:
    print(f"Communication error: {e}")
```

## Development

### Installation from Source

```bash
git clone https://github.com/gavinlouuu-kpt/severstar_mfc_rs485.git
cd severstar-mfc-rs485
pip install -e .
```

### Running Tests

```bash
python -m pytest tests/ -v
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues and questions, please open an issue on the [GitHub repository](https://github.com/gavinlouuu-kpt/severstar_mfc_rs485/issues).

## Acknowledgments

- Beijing Sevenstar Flow Co., Ltd. for the CS series MFC devices and protocol documentation
- PySerial team for excellent serial communication library
- Typer team for the wonderful CLI framework

---

*This package is not affiliated with or endorsed by Beijing Sevenstar Flow Co., Ltd.*
