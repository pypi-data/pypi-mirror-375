"""Command implementations for Severstar MFC devices."""

import struct
from typing import Optional, Union
from .protocol import (
    ProtocolMessage, ServiceType, CommandClass, ControlMode, DataFormat,
    create_read_command, create_write_command
)
from .communication import MFCCommunicator
from .exceptions import DeviceNotFoundError, InvalidParameterError


class MFCCommands:
    """High-level command interface for Severstar MFC devices."""
    
    def __init__(self, communicator: MFCCommunicator, address: int = 0x20):
        """
        Initialize MFC commands interface.
        
        Args:
            communicator: MFCCommunicator instance
            address: Device address (0x20 to 0x5F)
        """
        self.comm = communicator
        self.address = address
        self._validate_address(address)
    
    def _validate_address(self, address: int) -> None:
        """Validate device address range."""
        if not (0x20 <= address <= 0x5F):
            raise InvalidParameterError(f"Invalid device address: {address}. Must be between 0x20 and 0x5F")
    
    # Control Mode Commands
    def get_control_mode(self) -> ControlMode:
        """Get current control mode."""
        message = create_read_command(
            self.address, CommandClass.CONTROL, 0x01, 0x07
        )
        response = self.comm.send_message(message)
        return ControlMode(struct.unpack('B', response.data)[0])
    
    def set_control_mode(self, mode: ControlMode) -> None:
        """Set control mode."""
        message = create_write_command(
            self.address, CommandClass.CONTROL, 0x01, 0x07, mode.value
        )
        self.comm.send_message(message)
    
    # Setpoint Commands
    def get_setpoint(self) -> float:
        """Get current setpoint as fraction of full scale."""
        message = create_read_command(
            self.address, CommandClass.CONTROL, 0x01, 0x06
        )
        response = self.comm.send_message(message)
        value = struct.unpack('>I', response.data)[0]
        return DataFormat.fixed16_16_to_float(value)
    
    def set_setpoint(self, setpoint: float) -> None:
        """Set flow setpoint as fraction of full scale (-1 to 1)."""
        if not (-1.0 <= setpoint <= 1.0):
            raise InvalidParameterError("Setpoint must be between -1.0 and 1.0")
        
        value = DataFormat.float_to_fixed16_16(setpoint)
        message = create_write_command(
            self.address, CommandClass.CONTROL, 0x01, 0x06, value
        )
        self.comm.send_message(message)
    
    # Flow Reading Commands
    def get_flow_rate(self) -> float:
        """Get current flow rate as fraction of full scale."""
        message = create_read_command(
            self.address, CommandClass.CONTROL, 0x01, 0x05
        )
        response = self.comm.send_message(message)
        value = struct.unpack('>I', response.data)[0]
        return DataFormat.fixed16_16_to_float(value)
    
    def get_null_value(self) -> float:
        """Get customer null value."""
        message = create_read_command(
            self.address, CommandClass.ZEROING, 0x01, 0x07
        )
        response = self.comm.send_message(message)
        value = struct.unpack('>I', response.data)[0]
        return DataFormat.fixed16_16_to_float(value)
    
    def set_null_value(self, null_value: float) -> None:
        """Set customer null value."""
        if not (-1.0 <= null_value <= 1.0):
            raise InvalidParameterError("Null value must be between -1.0 and 1.0")
        
        value = DataFormat.float_to_fixed16_16(null_value)
        message = create_write_command(
            self.address, CommandClass.ZEROING, 0x01, 0x07, value
        )
        self.comm.send_message(message)
    
    # Valve Commands
    def get_valve_output(self) -> float:
        """Get current valve output as fraction (0 to 0.9999)."""
        message = create_read_command(
            self.address, CommandClass.CONTROL, 0x01, 0x08
        )
        response = self.comm.send_message(message)
        value = struct.unpack('>H', response.data)[0]
        return DataFormat.ufrac16_to_float(value)
    
    def set_valve_output(self, valve_output: float) -> None:
        """Set valve output as fraction (0 to 0.9999)."""
        if not (0.0 <= valve_output <= 0.9999):
            raise InvalidParameterError("Valve output must be between 0.0 and 0.9999")
        
        value = DataFormat.float_to_ufrac16(valve_output)
        message = create_write_command(
            self.address, CommandClass.CONTROL, 0x01, 0x08, value
        )
        self.comm.send_message(message)
    
    # Cumulative Flow Commands
    def get_totalizer(self) -> float:
        """Get total accumulated flow."""
        message = create_read_command(
            self.address, CommandClass.CONTROL, 0x01, 0x09
        )
        response = self.comm.send_message(message)
        return struct.unpack('>f', response.data)[0]
    
    def reset_totalizer(self) -> None:
        """Reset total accumulated flow."""
        message = create_write_command(
            self.address, CommandClass.CONTROL, 0x01, 0x09, 1
        )
        self.comm.send_message(message)
    
    def get_totalizer_time(self) -> int:
        """Get total operating time in seconds."""
        message = create_read_command(
            self.address, CommandClass.CONTROL, 0x01, 0x0A
        )
        response = self.comm.send_message(message)
        return struct.unpack('>I', response.data)[0]
    
    # Alarm Commands
    def get_alarm_status(self) -> int:
        """Get alarm status bitmask."""
        message = create_read_command(
            self.address, CommandClass.ALARM, 0x01, 0x07
        )
        response = self.comm.send_message(message)
        return struct.unpack('B', response.data)[0]
    
    def get_alarm_configuration(self) -> int:
        """Get alarm configuration bitmask."""
        message = create_read_command(
            self.address, CommandClass.ALARM, 0x01, 0x08
        )
        response = self.comm.send_message(message)
        return struct.unpack('B', response.data)[0]
    
    def set_alarm_configuration(self, config: int) -> None:
        """Set alarm configuration bitmask."""
        message = create_write_command(
            self.address, CommandClass.ALARM, 0x01, 0x08, config
        )
        self.comm.send_message(message)
    
    # Product Identification Commands
    def get_serial_number(self) -> str:
        """Get device serial number."""
        message = create_read_command(
            self.address, CommandClass.PRODUCT_ID, 0x01, 0x03
        )
        response = self.comm.send_message(message)
        return response.data.decode('ascii').strip('\x00')
    
    def get_model_number(self) -> str:
        """Get device model number."""
        message = create_read_command(
            self.address, CommandClass.PRODUCT_ID, 0x01, 0x04
        )
        response = self.comm.send_message(message)
        return response.data.decode('ascii').strip('\x00')
    
    def get_firmware_version(self) -> str:
        """Get firmware version."""
        message = create_read_command(
            self.address, CommandClass.PRODUCT_ID, 0x01, 0x05
        )
        response = self.comm.send_message(message)
        return response.data.decode('ascii').strip('\x00')
    
    # Calibration Data Commands
    def get_full_scale_flow(self) -> float:
        """Get full scale flow rate."""
        message = create_read_command(
            self.address, CommandClass.CALIBRATION, 0x01, 0x03
        )
        response = self.comm.send_message(message)
        return struct.unpack('>f', response.data)[0]
    
    def get_zero_flow(self) -> float:
        """Get zero flow calibration value."""
        message = create_read_command(
            self.address, CommandClass.CALIBRATION, 0x01, 0x04
        )
        response = self.comm.send_message(message)
        return struct.unpack('>f', response.data)[0]
    
    # Gas Information Commands
    def get_gas_type(self) -> int:
        """Get gas type identifier."""
        message = create_read_command(
            self.address, CommandClass.CALIBRATION, 0x01, 0x05
        )
        response = self.comm.send_message(message)
        return struct.unpack('B', response.data)[0]
    
    def get_gas_conversion_factor(self) -> float:
        """Get gas conversion factor."""
        message = create_read_command(
            self.address, CommandClass.CALIBRATION, 0x01, 0x06
        )
        response = self.comm.send_message(message)
        return struct.unpack('>f', response.data)[0]
    
    # Temperature Commands
    def get_sensor_temperature(self) -> float:
        """Get sensor temperature in Celsius."""
        message = create_read_command(
            self.address, CommandClass.TEMPERATURE, 0x01, 0x06
        )
        response = self.comm.send_message(message)
        value = struct.unpack('>H', response.data)[0]
        return DataFormat.temperature_to_float(value)
    
    def get_environment_temperature(self) -> float:
        """Get environment temperature in Celsius."""
        message = create_read_command(
            self.address, CommandClass.TEMPERATURE, 0x01, 0x07
        )
        response = self.comm.send_message(message)
        value = struct.unpack('>H', response.data)[0]
        return DataFormat.temperature_to_float(value)
    
    # Communication Configuration Commands
    def get_mac_address(self) -> int:
        """Get RS485 MAC address."""
        message = create_read_command(
            self.address, CommandClass.COMMUNICATION, 0x01, 0x01
        )
        response = self.comm.send_message(message)
        return struct.unpack('B', response.data)[0]
    
    def set_mac_address(self, address: int) -> None:
        """Set RS485 MAC address (32-94)."""
        if not (32 <= address <= 94):
            raise InvalidParameterError("MAC address must be between 32 and 94")
        
        message = create_write_command(
            self.address, CommandClass.COMMUNICATION, 0x01, 0x01, address
        )
        self.comm.send_message(message)
    
    def get_baud_rate(self) -> int:
        """Get RS485 baud rate."""
        message = create_read_command(
            self.address, CommandClass.COMMUNICATION, 0x01, 0x02
        )
        response = self.comm.send_message(message)
        return struct.unpack('>H', response.data)[0]
    
    def set_baud_rate(self, baudrate: int) -> None:
        """Set RS485 baud rate (1200, 2400, 4800, 9600, 19200)."""
        valid_baudrates = {1200, 2400, 4800, 9600, 19200}
        if baudrate not in valid_baudrates:
            raise InvalidParameterError(f"Baud rate must be one of {valid_baudrates}")
        
        message = create_write_command(
            self.address, CommandClass.COMMUNICATION, 0x01, 0x02, baudrate
        )
        self.comm.send_message(message)
    
    def reset_device(self) -> None:
        """Reset the device (required after EEPROM writes)."""
        message = create_write_command(
            self.address, CommandClass.COMMUNICATION, 0x01, 0x03, 1
        )
        self.comm.send_message(message)
