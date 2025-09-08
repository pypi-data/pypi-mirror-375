"""RS485 communication handling for Severstar MFC devices."""

import time
import serial
from typing import Optional, List
from .protocol import ProtocolMessage, ServiceType
from .exceptions import CommunicationError, TimeoutError, ChecksumError


class MFCCommunicator:
    """Handles RS485 communication with Severstar MFC devices."""
    
    def __init__(
        self,
        port: str,
        baudrate: int = 19200,
        timeout: float = 1.0,
        write_timeout: float = 1.0
    ):
        """
        Initialize the MFC communicator.
        
        Args:
            port: Serial port name (e.g., '/dev/ttyUSB0', 'COM3')
            baudrate: Baud rate (1200, 2400, 4800, 9600, 19200)
            timeout: Read timeout in seconds
            write_timeout: Write timeout in seconds
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.write_timeout = write_timeout
        self.serial_conn: Optional[serial.Serial] = None
    
    def connect(self) -> None:
        """Establish connection to the serial port."""
        try:
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=self.timeout,
                write_timeout=self.write_timeout
            )
            # Allow some time for the connection to stabilize
            time.sleep(0.1)
        except serial.SerialException as e:
            raise CommunicationError(f"Failed to connect to {self.port}: {e}")
    
    def disconnect(self) -> None:
        """Close the serial connection."""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
        self.serial_conn = None
    
    def is_connected(self) -> bool:
        """Check if the serial connection is open."""
        return self.serial_conn is not None and self.serial_conn.is_open
    
    def send_message(self, message: ProtocolMessage) -> ProtocolMessage:
        """
        Send a protocol message and receive the response.
        
        Args:
            message: ProtocolMessage to send
            
        Returns:
            ProtocolMessage response from the device
            
        Raises:
            CommunicationError: If communication fails
            TimeoutError: If no response is received within timeout
            ChecksumError: If response checksum is invalid
        """
        if not self.is_connected():
            raise CommunicationError("Not connected to serial port")
        
        # Encode the message to bytes
        message_bytes = message.encode()
        
        try:
            # Clear input buffer
            self.serial_conn.reset_input_buffer()
            
            # Send the message
            self.serial_conn.write(message_bytes)
            self.serial_conn.flush()
            
            # Read the response
            response_bytes = self._read_response()
            
            # Decode the response
            response = ProtocolMessage.decode(response_bytes)
            
            return response
            
        except serial.SerialTimeoutException:
            raise TimeoutError(f"Write timeout after {self.write_timeout} seconds")
        except serial.SerialException as e:
            raise CommunicationError(f"Serial communication error: {e}")
        except ValueError as e:
            raise ChecksumError(f"Invalid response format: {e}")
    
    def _read_response(self) -> bytes:
        """
        Read response from the serial port.
        
        Returns:
            bytes: Complete response message
            
        Raises:
            TimeoutError: If no response is received within timeout
        """
        start_time = time.time()
        response = bytearray()
        
        # Read until we have a complete message or timeout
        while time.time() - start_time < self.timeout:
            if self.serial_conn.in_waiting > 0:
                # Read available bytes
                chunk = self.serial_conn.read(self.serial_conn.in_waiting)
                response.extend(chunk)
                
                # Check if we have a complete message
                if self._is_complete_message(response):
                    return bytes(response)
            
            time.sleep(0.01)
        
        raise TimeoutError(f"No response received within {self.timeout} seconds")
    
    def _is_complete_message(self, data: bytearray) -> bool:
        """
        Check if the data contains a complete protocol message.
        
        Args:
            data: Received data bytes
            
        Returns:
            bool: True if complete message is present
        """
        if len(data) < 8:  # Minimum message length
            return False
        
        # Check STX byte
        if data[1] != 0x02:
            return False
        
        # Get data length from message
        data_length = data[3]
        
        # Calculate expected message length
        # Header (7 bytes) + data + pad (1 byte) + checksum (1 byte)
        expected_length = 7 + data_length + 2
        
        return len(data) >= expected_length
    
    def read_register(
        self,
        address: int,
        command_class: int,
        instance: int,
        attribute: int
    ) -> bytes:
        """
        Read a register from the MFC device.
        
        Args:
            address: Device address
            command_class: Command class identifier
            instance: Command instance identifier
            attribute: Command attribute identifier
            
        Returns:
            bytes: Raw data from the response
        """
        message = ProtocolMessage(
            address=address,
            service_type=ServiceType.READ,
            command_class=command_class,
            instance=instance,
            attribute=attribute
        )
        
        response = self.send_message(message)
        return response.data if response.data else b''
    
    def write_register(
        self,
        address: int,
        command_class: int,
        instance: int,
        attribute: int,
        data: bytes
    ) -> None:
        """
        Write to a register on the MFC device.
        
        Args:
            address: Device address
            command_class: Command class identifier
            instance: Command instance identifier
            attribute: Command attribute identifier
            data: Data to write
        """
        message = ProtocolMessage(
            address=address,
            service_type=ServiceType.WRITE,
            command_class=command_class,
            instance=instance,
            attribute=attribute,
            data=data
        )
        
        self.send_message(message)
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()


def discover_devices(
    port: str,
    baudrate: int = 19200,
    timeout: float = 0.1
) -> List[int]:
    """
    Discover MFC devices on the RS485 bus.
    
    Args:
        port: Serial port name
        baudrate: Baud rate for communication
        timeout: Response timeout per device
        
    Returns:
        List of discovered device addresses
    """
    discovered = []
    
    with MFCCommunicator(port, baudrate, timeout) as comm:
        # Try broadcast address first
        try:
            # Use product identification read command to discover devices
            message = ProtocolMessage(
                address=0xFF,  # Broadcast address
                service_type=ServiceType.READ,
                command_class=0x01,  # Product identification
                instance=0x01,
                attribute=0x03  # Serial number
            )
            
            response = comm.send_message(message)
            if response.address != 0x00:  # Valid response from a device
                discovered.append(response.address)
                
        except (TimeoutError, CommunicationError, ChecksumError):
            pass
        
        # If broadcast didn't work, try individual addresses
        if not discovered:
            for address in range(0x20, 0x60):  # Address range 0x20 to 0x5F
                try:
                    message = ProtocolMessage(
                        address=address,
                        service_type=ServiceType.READ,
                        command_class=0x01,  # Product identification
                        instance=0x01,
                        attribute=0x03  # Serial number
                    )
                    
                    response = comm.send_message(message)
                    if response.address == 0x00:  # Valid response
                        discovered.append(address)
                        
                except (TimeoutError, CommunicationError, ChecksumError):
                    continue
    
    return discovered
