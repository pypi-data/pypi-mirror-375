# CS Series MFC Communication Protocol Reference

## Overview
This document describes the RS-485 communication protocol for CS series digital mass flow controllers (MFCs) from Beijing Sevenstar Flow Co., Ltd. Protocol version: 2.3

## Communication Parameters

### RS-485 Settings
| Parameter | Value |
|-----------|-------|
| Start Bit | 1 |
| Data Bits | 8 |
| Parity | None |
| Stop Bit | 1 |
| Baud Rates | 1200, 2400, 4800, 9600, 19200 (default) |

### Address Range
- **Device addresses**: 0x20 (32) to 0x5F (95)
- **Reserved addresses**:
  - 0x00 (0): Bus master
  - 0xFF (255): General address (broadcast)
  - 0x01 (1) to 0x1F (31): Reserved for other functions

## Message Format

### Packet Structure
Each message consists of a fixed format data packet:

| Byte | Content | Description |
|------|---------|-------------|
| 1 | Address | Communication unit address |
| 2 | STX | Fixed value 0x02 |
| 3 | Service Type | 0x80 (read) or 0x81 (write) |
| 4 | Data Length | Length of data section minus 6 |
| 5 | Class | Command class identifier |
| 6 | Instance | Command instance identifier |
| 7 | Attribute | Command attribute identifier |
| 8...n-2 | Data | Command-specific data |
| n-1 | Pad Byte | Fixed value 0x00 |
| n | Checksum | 8-bit checksum |

### Data Types
- **FIXED16.16**: Fixed-point format, 16-bit integer + 16-bit fraction
- **UFRAC16**: Unsigned fractional 16-bit format
- **UINTXX**: Unsigned integer (various bit lengths)
- **TEXTXX**: Text string (various lengths)
- **FLOAT32**: 32-bit floating point

## Command Reference

### Control Mode

#### Read Control Mode
- **Command**: 0x80, Class: 0xA0, Instance: 0x01, Attribute: 0x07
- **Response**: UINT8 (0-255)
- **Values**:
  - 0: Closed loop
  - 1: Open loop
  - 2: Manual valve control

#### Write Control Mode
- **Command**: 0x81, Class: 0xA0, Instance: 0x01, Attribute: 0x07
- **Data**: UINT8 (0-2)

### Setpoint Commands

#### Read Setpoint
- **Command**: 0x80, Class: 0xA0, Instance: 0x01, Attribute: 0x06
- **Response**: FIXED16.16 (-1 to 1)
- **Format**: Value represents flow rate as fraction of full scale

#### Write Setpoint
- **Command**: 0x81, Class: 0xA0, Instance: 0x01, Attribute: 0x06
- **Data**: FIXED16.16 (-1 to 1)

### Zeroing and Flow Reading

#### Read Flow Rate
- **Command**: 0x80, Class: 0xA0, Instance: 0x01, Attribute: 0x05
- **Response**: FIXED16.16 (-1 to 1)
- **Format**: Current flow rate as fraction of full scale

#### Read Null Value
- **Command**: 0x80, Class: 0xA1, Instance: 0x01, Attribute: 0x07
- **Response**: FIXED16.16 (-1 to 1)
- **Description**: Customer zero point value

#### Write Null Value
- **Command**: 0x81, Class: 0xA1, Instance: 0x01, Attribute: 0x07
- **Data**: FIXED16.16 (-1 to 1)

### Valve Commands

#### Read Valve Output
- **Command**: 0x80, Class: 0xA0, Instance: 0x01, Attribute: 0x08
- **Response**: UFRAC16 (0 to 0.9999)
- **Format**: Valve position as fraction

#### Write Valve Output
- **Command**: 0x81, Class: 0xA0, Instance: 0x01, Attribute: 0x08
- **Data**: UFRAC16 (0 to 0.9999)

### Cumulative Flow

#### Read Totalizer
- **Command**: 0x80, Class: 0xA0, Instance: 0x01, Attribute: 0x09
- **Response**: FLOAT32
- **Format**: Total accumulated flow

#### Reset Totalizer
- **Command**: 0x81, Class: 0xA0, Instance: 0x01, Attribute: 0x09
- **Data**: UINT8 (1 to reset)

#### Read Totalizer Time
- **Command**: 0x80, Class: 0xA0, Instance: 0x01, Attribute: 0x0A
- **Response**: UINT32
- **Format**: Total operating time in seconds

### Alarms

#### Read Alarm Status
- **Command**: 0x80, Class: 0xA2, Instance: 0x01, Attribute: 0x07
- **Response**: UINT8 (bitmask)
- **Bits**:
  - 0: Flow alarm
  - 1: Temperature alarm
  - 2: Valve alarm
  - 3: Sensor alarm

#### Read Alarm Configuration
- **Command**: 0x80, Class: 0xA2, Instance: 0x01, Attribute: 0x08
- **Response**: UINT8 (bitmask)
- **Format**: Alarm enable/disable configuration

#### Write Alarm Configuration
- **Command**: 0x81, Class: 0xA2, Instance: 0x01, Attribute: 0x08
- **Data**: UINT8 (bitmask)

### Product Identification

#### Read Serial Number
- **Command**: 0x80, Class: 0x01, Instance: 0x01, Attribute: 0x03
- **Response**: TEXT16
- **Format**: Device serial number

#### Read Model Number
- **Command**: 0x80, Class: 0x01, Instance: 0x01, Attribute: 0x04
- **Response**: TEXT16
- **Format**: Device model number

#### Read Firmware Version
- **Command**: 0x80, Class: 0x01, Instance: 0x01, Attribute: 0x05
- **Response**: TEXT8
- **Format**: Firmware version string

### Calibration Data

#### Read Full Scale Flow
- **Command**: 0x80, Class: 0x02, Instance: 0x01, Attribute: 0x03
- **Response**: FLOAT32
- **Format**: Full scale flow rate

#### Read Zero Flow
- **Command**: 0x80, Class: 0x02, Instance: 0x01, Attribute: 0x04
- **Response**: FLOAT32
- **Format**: Zero flow calibration value

### Gas Information

#### Read Gas Type
- **Command**: 0x80, Class: 0x02, Instance: 0x01, Attribute: 0x05
- **Response**: UINT8
- **Values**: Gas type identifier

#### Read Gas Conversion Factor
- **Command**: 0x80, Class: 0x02, Instance: 0x01, Attribute: 0x06
- **Response**: FLOAT32
- **Format**: Gas conversion factor

### Sensor Information

#### Read Sensor Temperature
- **Command**: 0x80, Class: 0xA3, Instance: 0x01, Attribute: 0x06
- **Response**: UINT16
- **Conversion**: Temperature (°C) = Value * 0.0806 - 50

### Environment Temperature

#### Read Environment Temperature
- **Command**: 0x80, Class: 0xA3, Instance: 0x01, Attribute: 0x07
- **Response**: UINT16
- **Conversion**: Temperature (°C) = Value * 0.0806 - 50

### MAC Address, Baud Rate, and Reset

#### Read MAC Address
- **Command**: 0x80, Class: 0x03, Instance: 0x01, Attribute: 0x01
- **Response**: UINT8 (32-94)

#### Write MAC Address
- **Command**: 0x81, Class: 0x03, Instance: 0x01, Attribute: 0x01
- **Data**: UINT8 (32-94)

#### Read Baud Rate
- **Command**: 0x80, Class: 0x03, Instance: 0x01, Attribute: 0x02
- **Response**: UINT16 (1200, 2400, 4800, 9600, 19200)

#### Write Baud Rate
- **Command**: 0x81, Class: 0x03, Instance: 0x01, Attribute: 0x02
- **Data**: UINT16 (1200, 2400, 4800, 9600, 19200)

#### Reset Device
- **Command**: 0x81, Class: 0x03, Instance: 0x01, Attribute: 0x03
- **Data**: UINT8 (1)
- **Note**: Required after EEPROM write operations

## Checksum Calculation
The checksum is an 8-bit value calculated over all bytes of the message except the checksum byte itself.

## Examples

### Read Flow Rate Example
```
Address: 0x20
STX: 0x02
Service: 0x80 (read)
Data Length: 0x03
Class: 0xA0
Instance: 0x01
Attribute: 0x05
Pad: 0x00
Checksum: [calculated]
```

### Response Example
```
Address: 0x00
STX: 0x02
Service: 0x80 (read)
Data Length: 0x05
Class: 0xA0
Instance: 0x01
Attribute: 0x05
Data: [FIXED16.16 flow value]
Pad: 0x00
Checksum: [calculated]
```

## Notes
- All write operations to EEPROM require a device reset to take effect
- The protocol supports broadcast address 0xFF for device discovery
- Baud rate changes take effect immediately after confirmation
- Temperature values use the conversion formula: °C = Value * 0.0806 - 50

---

*Document generated from CS系列MFC通讯协议V2.3.pdf - Beijing Sevenstar Flow Co., Ltd.*
