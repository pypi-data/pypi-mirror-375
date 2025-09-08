"""Top-level package for Severstar MFC RS485 Control."""

from .severstar_mfc_rs485 import SeverstarMFC, discover_mfc_devices, create_mfc_connection
from .protocol import ServiceType, CommandClass, ControlMode, DataFormat, ProtocolMessage
from .communication import MFCCommunicator, discover_devices
from .commands import MFCCommands
from .exceptions import (
    SeverstarError, CommunicationError, TimeoutError, ChecksumError,
    ProtocolError, DeviceNotFoundError, InvalidParameterError,
    ConfigurationError, CalibrationError, ValveError, SensorError
)

__author__ = """Gavin Lou"""
__email__ = 'gavinlou@kingsphase.page'

__all__ = [
    'SeverstarMFC',
    'MFCCommunicator',
    'MFCCommands',
    'ServiceType',
    'CommandClass',
    'ControlMode',
    'DataFormat',
    'ProtocolMessage',
    'discover_mfc_devices',
    'discover_devices',
    'create_mfc_connection',
    'SeverstarError',
    'CommunicationError',
    'TimeoutError',
    'ChecksumError',
    'ProtocolError',
    'DeviceNotFoundError',
    'InvalidParameterError',
    'ConfigurationError',
    'CalibrationError',
    'ValveError',
    'SensorError'
]
