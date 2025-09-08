"""Custom exceptions for Severstar MFC RS485 communication."""


class SeverstarError(Exception):
    """Base exception for all Severstar MFC errors."""
    pass


class CommunicationError(SeverstarError):
    """Raised when communication with the device fails."""
    pass


class TimeoutError(SeverstarError):
    """Raised when a communication timeout occurs."""
    pass


class ChecksumError(SeverstarError):
    """Raised when a message checksum is invalid."""
    pass


class ProtocolError(SeverstarError):
    """Raised when protocol parsing fails."""
    pass


class DeviceNotFoundError(SeverstarError):
    """Raised when a device is not found at the specified address."""
    pass


class InvalidParameterError(SeverstarError):
    """Raised when an invalid parameter is provided."""
    pass


class ConfigurationError(SeverstarError):
    """Raised when device configuration is invalid."""
    pass


class CalibrationError(SeverstarError):
    """Raised when calibration operations fail."""
    pass


class ValveError(SeverstarError):
    """Raised when valve operations fail."""
    pass


class SensorError(SeverstarError):
    """Raised when sensor readings are invalid."""
    pass
