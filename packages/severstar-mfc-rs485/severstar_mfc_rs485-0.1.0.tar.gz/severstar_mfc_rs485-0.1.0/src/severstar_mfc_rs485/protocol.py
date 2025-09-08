"""Protocol message encoding and decoding for Severstar MFC RS485 communication."""

import struct
from typing import Tuple, Union, List, Optional
from enum import IntEnum


class ServiceType(IntEnum):
    """Service types for protocol messages."""
    READ = 0x80
    WRITE = 0x81


class CommandClass(IntEnum):
    """Command class identifiers."""
    PRODUCT_ID = 0x01
    CALIBRATION = 0x02
    COMMUNICATION = 0x03
    CONTROL = 0xA0
    ZEROING = 0xA1
    ALARM = 0xA2
    TEMPERATURE = 0xA3


class ControlMode(IntEnum):
    """Control mode values."""
    CLOSED_LOOP = 0
    OPEN_LOOP = 1
    MANUAL_VALVE = 2


class DataFormat:
    """Data format conversion utilities."""
    
    @staticmethod
    def fixed16_16_to_float(value: int) -> float:
        """Convert FIXED16.16 format to float."""
        integer_part = (value >> 16) & 0xFFFF
        fractional_part = value & 0xFFFF
        if integer_part & 0x8000:  # Negative number
            integer_part = integer_part - 0x10000
        return integer_part + fractional_part / 65536.0
    
    @staticmethod
    def float_to_fixed16_16(value: float) -> int:
        """Convert float to FIXED16.16 format."""
        integer_part = int(value)
        fractional_part = int((value - integer_part) * 65536)
        if integer_part < 0:
            integer_part = integer_part & 0xFFFF
        return (integer_part << 16) | fractional_part
    
    @staticmethod
    def ufrac16_to_float(value: int) -> float:
        """Convert UFRAC16 format to float."""
        return value / 65536.0
    
    @staticmethod
    def float_to_ufrac16(value: float) -> int:
        """Convert float to UFRAC16 format."""
        return int(value * 65536)
    
    @staticmethod
    def temperature_to_float(value: int) -> float:
        """Convert temperature value to Celsius."""
        return value * 0.0806 - 50
    
    @staticmethod
    def float_to_temperature(value: float) -> int:
        """Convert Celsius to temperature value."""
        return int((value + 50) / 0.0806)


class ProtocolMessage:
    """Represents a protocol message for Severstar MFC communication."""
    
    def __init__(
        self,
        address: int,
        service_type: ServiceType,
        command_class: CommandClass,
        instance: int,
        attribute: int,
        data: Optional[Union[bytes, int, float, str]] = None
    ):
        self.address = address
        self.service_type = service_type
        self.command_class = command_class
        self.instance = instance
        self.attribute = attribute
        self.data = data
        self.pad_byte = 0x00
    
    def encode(self) -> bytes:
        """Encode the message to bytes."""
        # Convert data to bytes based on type
        data_bytes = self._convert_data_to_bytes()
        
        # Calculate data length (data length minus 6)
        data_length = len(data_bytes) if data_bytes else 0
        
        # Build message header
        message = bytearray()
        message.append(self.address)
        message.append(0x02)  # STX
        message.append(self.service_type)
        message.append(data_length)
        message.append(self.command_class)
        message.append(self.instance)
        message.append(self.attribute)
        
        # Add data if present
        if data_bytes:
            message.extend(data_bytes)
        
        # Add pad byte
        message.append(self.pad_byte)
        
        # Calculate and add checksum
        checksum = self._calculate_checksum(message)
        message.append(checksum)
        
        return bytes(message)
    
    def _convert_data_to_bytes(self) -> Optional[bytes]:
        """Convert data to appropriate byte format."""
        if self.data is None:
            return None
        
        if isinstance(self.data, bytes):
            return self.data
        
        if isinstance(self.data, int):
            # Determine appropriate size based on value
            if 0 <= self.data <= 0xFF:
                return struct.pack('B', self.data)
            elif 0 <= self.data <= 0xFFFF:
                return struct.pack('>H', self.data)
            elif 0 <= self.data <= 0xFFFFFFFF:
                return struct.pack('>I', self.data)
            else:
                raise ValueError(f"Integer value {self.data} out of supported range")
        
        if isinstance(self.data, float):
            # Assume FLOAT32 for floats
            return struct.pack('>f', self.data)
        
        if isinstance(self.data, str):
            # Convert string to bytes
            return self.data.encode('ascii')
        
        raise ValueError(f"Unsupported data type: {type(self.data)}")
    
    def _calculate_checksum(self, message: bytearray) -> int:
        """Calculate 8-bit checksum for the message."""
        checksum = 0
        for byte in message:
            checksum = (checksum + byte) & 0xFF
        return checksum
    
    @classmethod
    def decode(cls, message_bytes: bytes) -> 'ProtocolMessage':
        """Decode bytes into a ProtocolMessage."""
        if len(message_bytes) < 8:
            raise ValueError("Message too short")
        
        # Verify checksum
        calculated_checksum = cls._calculate_checksum(bytearray(message_bytes[:-1]))
        if calculated_checksum != message_bytes[-1]:
            raise ValueError("Checksum mismatch")
        
        address = message_bytes[0]
        stx = message_bytes[1]
        if stx != 0x02:
            raise ValueError("Invalid STX byte")
        
        service_type = ServiceType(message_bytes[2])
        data_length = message_bytes[3]
        command_class = CommandClass(message_bytes[4])
        instance = message_bytes[5]
        attribute = message_bytes[6]
        
        # Extract data
        data_start = 7
        data_end = data_start + data_length
        data_bytes = message_bytes[data_start:data_end] if data_length > 0 else None
        
        # Verify pad byte
        pad_byte = message_bytes[data_end] if data_length > 0 else message_bytes[7]
        if pad_byte != 0x00:
            raise ValueError("Invalid pad byte")
        
        return cls(
            address=address,
            service_type=service_type,
            command_class=command_class,
            instance=instance,
            attribute=attribute,
            data=data_bytes
        )
    
    @staticmethod
    def _calculate_checksum(message: bytearray) -> int:
        """Calculate 8-bit checksum for the message."""
        checksum = 0
        for byte in message:
            checksum = (checksum + byte) & 0xFF
        return checksum


# Command builder functions for common operations
def create_read_command(
    address: int,
    command_class: CommandClass,
    instance: int,
    attribute: int
) -> ProtocolMessage:
    """Create a read command message."""
    return ProtocolMessage(
        address=address,
        service_type=ServiceType.READ,
        command_class=command_class,
        instance=instance,
        attribute=attribute
    )


def create_write_command(
    address: int,
    command_class: CommandClass,
    instance: int,
    attribute: int,
    data: Union[bytes, int, float, str]
) -> ProtocolMessage:
    """Create a write command message."""
    return ProtocolMessage(
        address=address,
        service_type=ServiceType.WRITE,
        command_class=command_class,
        instance=instance,
        attribute=attribute,
        data=data
    )
