"""Main module for Severstar MFC RS485 communication."""

from typing import Optional
from .communication import MFCCommunicator, discover_devices
from .commands import MFCCommands
from .protocol import ControlMode
from .exceptions import SeverstarError, CommunicationError, TimeoutError


class SeverstarMFC:
    """High-level interface for Severstar MFC devices."""
    
    def __init__(
        self,
        port: str,
        address: int = 0x20,
        baudrate: int = 19200,
        timeout: float = 1.0
    ):
        """
        Initialize Severstar MFC interface.
        
        Args:
            port: Serial port name (e.g., '/dev/ttyUSB0', 'COM3')
            address: Device address (0x20 to 0x5F)
            baudrate: Baud rate (1200, 2400, 4800, 9600, 19200)
            timeout: Communication timeout in seconds
        """
        self.communicator = MFCCommunicator(port, baudrate, timeout)
        self.commands = MFCCommands(self.communicator, address)
    
    def connect(self) -> None:
        """Establish connection to the MFC device."""
        self.communicator.connect()
    
    def disconnect(self) -> None:
        """Close the connection to the MFC device."""
        self.communicator.disconnect()
    
    def is_connected(self) -> bool:
        """Check if connected to the MFC device."""
        return self.communicator.is_connected()
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
    
    # High-level convenience methods
    def get_device_info(self) -> dict:
        """Get comprehensive device information."""
        return {
            'serial_number': self.commands.get_serial_number(),
            'model_number': self.commands.get_model_number(),
            'firmware_version': self.commands.get_firmware_version(),
            'mac_address': self.commands.get_mac_address(),
            'baud_rate': self.commands.get_baud_rate()
        }
    
    def get_status(self) -> dict:
        """Get current device status."""
        return {
            'control_mode': self.commands.get_control_mode().name,
            'setpoint': self.commands.get_setpoint(),
            'flow_rate': self.commands.get_flow_rate(),
            'valve_output': self.commands.get_valve_output(),
            'alarm_status': self.commands.get_alarm_status(),
            'sensor_temperature': self.commands.get_sensor_temperature(),
            'environment_temperature': self.commands.get_environment_temperature()
        }
    
    def get_calibration_info(self) -> dict:
        """Get calibration information."""
        return {
            'full_scale_flow': self.commands.get_full_scale_flow(),
            'zero_flow': self.commands.get_zero_flow(),
            'gas_type': self.commands.get_gas_type(),
            'gas_conversion_factor': self.commands.get_gas_conversion_factor(),
            'null_value': self.commands.get_null_value()
        }
    
    def get_totalizer_info(self) -> dict:
        """Get totalizer information."""
        return {
            'total_flow': self.commands.get_totalizer(),
            'operating_time': self.commands.get_totalizer_time()
        }
    
    # Shortcut methods for common operations
    def set_flow_rate(self, flow_rate: float) -> None:
        """Set flow rate as fraction of full scale (-1 to 1)."""
        self.commands.set_setpoint(flow_rate)
    
    def get_flow_rate(self) -> float:
        """Get current flow rate as fraction of full scale."""
        return self.commands.get_flow_rate()
    
    def set_control_mode(self, mode: ControlMode) -> None:
        """Set control mode."""
        self.commands.set_control_mode(mode)
    
    def get_control_mode(self) -> ControlMode:
        """Get current control mode."""
        return self.commands.get_control_mode()


# Module-level convenience functions
def discover_mfc_devices(port: str, baudrate: int = 19200) -> list:
    """
    Discover MFC devices on the RS485 bus.
    
    Args:
        port: Serial port name
        baudrate: Baud rate for discovery
        
    Returns:
        List of discovered device addresses
    """
    return discover_devices(port, baudrate)


def create_mfc_connection(
    port: str,
    address: int = 0x20,
    baudrate: int = 19200
) -> SeverstarMFC:
    """
    Create and connect to a Severstar MFC device.
    
    Args:
        port: Serial port name
        address: Device address
        baudrate: Baud rate
        
    Returns:
        Connected SeverstarMFC instance
    """
    mfc = SeverstarMFC(port, address, baudrate)
    mfc.connect()
    return mfc
