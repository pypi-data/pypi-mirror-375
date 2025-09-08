# Severstar MFC RS485 Python Package - Usage Guide

## Installation

```bash
pip install severstar-mfc-rs485
```

## Quick Start

### Basic Usage

```python
from severstar_mfc_rs485 import SeverstarMFC, discover_mfc_devices

# Discover devices on the RS485 bus
devices = discover_mfc_devices('/dev/ttyUSB0')
print(f"Discovered devices: {devices}")

# Connect to a specific device
with SeverstarMFC('/dev/ttyUSB0', address=32) as mfc:
    # Get device information
    info = mfc.get_device_info()
    print(f"Serial number: {info['serial_number']}")
    
    # Get current status
    status = mfc.get_status()
    print(f"Flow rate: {status['flow_rate']:.4f} FS")
    
    # Set flow rate to 50% of full scale
    mfc.set_flow_rate(0.5)
```

### Command Line Interface

The package includes a comprehensive CLI tool:

```bash
# Discover devices
severstar_mfc_rs485 discover /dev/ttyUSB0

# Get device information
severstar_mfc_rs485 info /dev/ttyUSB0 --address 32

# Get device status
severstar_mfc_rs485 status /dev/ttyUSB0 --address 32

# Set flow rate
severstar_mfc_rs485 set-flow /dev/ttyUSB0 0.5 --address 32

# Get flow rate
severstar_mfc_rs485 get-flow /dev/ttyUSB0 --address 32

# Set control mode
severstar_mfc_rs485 set-mode /dev/ttyUSB0 closed_loop --address 32

# Get calibration information
severstar_mfc_rs485 calibration /dev/ttyUSB0 --address 32

# Get totalizer information
severstar_mfc_rs485 totalizer /dev/ttyUSB0 --address 32

# Reset totalizer
severstar_mfc_rs485 reset-totalizer /dev/ttyUSB0 --address 32
```

## API Reference

### Main Classes

#### SeverstarMFC
High-level interface for MFC devices.

```python
mfc = SeverstarMFC(port, address=32, baudrate=19200, timeout=1.0)
mfc.connect()
mfc.disconnect()
mfc.is_connected()
```

#### MFCCommunicator
Low-level RS485 communication handler.

```python
comm = MFCCommunicator(port, baudrate=19200, timeout=1.0)
comm.connect()
comm.send_message(message)
```

#### MFCCommands
Command-level interface for specific operations.

```python
commands = MFCCommands(communicator, address=32)
commands.get_flow_rate()
commands.set_setpoint(0.5)
```

### Common Operations

#### Device Discovery
```python
from severstar_mfc_rs485 import discover_mfc_devices

devices = discover_mfc_devices('/dev/ttyUSB0')
# Returns list of device addresses [32, 33, 34, ...]
```

#### Reading Device Information
```python
with SeverstarMFC('/dev/ttyUSB0', 32) as mfc:
    info = mfc.get_device_info()
    # Contains: serial_number, model_number, firmware_version, mac_address, baud_rate
```

#### Reading Status
```python
with SeverstarMFC('/dev/ttyUSB0', 32) as mfc:
    status = mfc.get_status()
    # Contains: control_mode, setpoint, flow_rate, valve_output, 
    #           alarm_status, sensor_temperature, environment_temperature
```

#### Setting Flow Rate
```python
with SeverstarMFC('/dev/ttyUSB0', 32) as mfc:
    mfc.set_flow_rate(0.75)  # 75% of full scale
```

#### Control Modes
```python
from severstar_mfc_rs485 import ControlMode

with SeverstarMFC('/dev/ttyUSB0', 32) as mfc:
    mfc.set_control_mode(ControlMode.CLOSED_LOOP)
    # or ControlMode.OPEN_LOOP, ControlMode.MANUAL_VALVE
```

### Error Handling

The package provides comprehensive exception handling:

```python
from severstar_mfc_rs485 import (
    CommunicationError, TimeoutError, ChecksumError,
    DeviceNotFoundError, InvalidParameterError
)

try:
    with SeverstarMFC('/dev/ttyUSB0', 32) as mfc:
        mfc.set_flow_rate(2.0)  # Invalid value (>1.0)
except InvalidParameterError as e:
    print(f"Invalid parameter: {e}")
except CommunicationError as e:
    print(f"Communication error: {e}")
except TimeoutError as e:
    print(f"Timeout error: {e}")
```

### Advanced Usage

#### Direct Protocol Access
```python
from severstar_mfc_rs485 import ProtocolMessage, ServiceType, CommandClass

# Create a custom read command
message = ProtocolMessage(
    address=32,
    service_type=ServiceType.READ,
    command_class=CommandClass.CONTROL,
    instance=0x01,
    attribute=0x05  # Flow rate
)

# Send using communicator
with MFCCommunicator('/dev/ttyUSB0') as comm:
    response = comm.send_message(message)
    print(f"Response data: {response.data}")
```

#### Data Format Conversions
```python
from severstar_mfc_rs485 import DataFormat

# Convert float to FIXED16.16 format
fixed_value = DataFormat.float_to_fixed16_16(1.5)

# Convert FIXED16.16 to float
float_value = DataFormat.fixed16_16_to_float(fixed_value)

# Temperature conversions
temp_value = DataFormat.float_to_temperature(25.0)  # Celsius to device value
celsius = DataFormat.temperature_to_float(temp_value)  # Device value to Celsius
```

## Examples

### Monitoring Application
```python
import time
from severstar_mfc_rs485 import SeverstarMFC

def monitor_mfc(port, address, interval=1.0):
    with SeverstarMFC(port, address) as mfc:
        while True:
            status = mfc.get_status()
            print(f"Flow: {status['flow_rate']:.4f} FS | "
                  f"Temp: {status['sensor_temperature']:.1f}°C | "
                  f"Valve: {status['valve_output']:.4f}")
            time.sleep(interval)

# Monitor device at address 32
monitor_mfc('/dev/ttyUSB0', 32)
```

### Batch Control
```python
from severstar_mfc_rs485 import SeverstarMFC

def run_flow_profile(port, address, profile):
    with SeverstarMFC(port, address) as mfc:
        for flow_rate, duration in profile:
            mfc.set_flow_rate(flow_rate)
            print(f"Set flow to {flow_rate:.3f} FS for {duration}s")
            time.sleep(duration)

# Run a flow profile
profile = [
    (0.0, 2.0),    # 0% for 2 seconds
    (0.5, 5.0),    # 50% for 5 seconds  
    (0.8, 3.0),    # 80% for 3 seconds
    (0.0, 1.0)     # Back to 0%
]

run_flow_profile('/dev/ttyUSB0', 32, profile)
```

## Troubleshooting

### Common Issues

1. **Device not found**: Check RS485 connections and device address
2. **Communication errors**: Verify baud rate settings (default: 19200)
3. **Timeout errors**: Increase timeout parameter or check cable connections
4. **Checksum errors**: May indicate electrical noise or connection issues

### Debug Mode

Enable debug logging to see raw communication:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Supported Devices

This package supports CS series digital mass flow controllers from Beijing Sevenstar Flow Co., Ltd., including:

- CS100 series
- CS200 series  
- Other CS series devices with RS485 interface

Refer to the protocol reference for detailed command specifications.
