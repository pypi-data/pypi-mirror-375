"""Basic tests for Severstar MFC RS485 package."""

import pytest
from severstar_mfc_rs485 import (
    ServiceType, CommandClass, ControlMode, DataFormat, ProtocolMessage,
    SeverstarError, CommunicationError
)


def test_protocol_enums():
    """Test that protocol enums are properly defined."""
    assert ServiceType.READ == 0x80
    assert ServiceType.WRITE == 0x81
    
    assert CommandClass.PRODUCT_ID == 0x01
    assert CommandClass.CONTROL == 0xA0
    
    assert ControlMode.CLOSED_LOOP == 0
    assert ControlMode.OPEN_LOOP == 1
    assert ControlMode.MANUAL_VALVE == 2


def test_data_format_conversions():
    """Test data format conversion functions."""
    # Test FIXED16.16 conversions
    test_value = 1.5
    fixed = DataFormat.float_to_fixed16_16(test_value)
    converted = DataFormat.fixed16_16_to_float(fixed)
    assert abs(converted - test_value) < 0.0001
    
    # Test UFRAC16 conversions
    test_frac = 0.75
    ufrac = DataFormat.float_to_ufrac16(test_frac)
    converted_frac = DataFormat.ufrac16_to_float(ufrac)
    assert abs(converted_frac - test_frac) < 0.0001
    
    # Test temperature conversions
    test_temp = 25.0
    temp_val = DataFormat.float_to_temperature(test_temp)
    converted_temp = DataFormat.temperature_to_float(temp_val)
    assert abs(converted_temp - test_temp) < 0.1


def test_protocol_message_creation():
    """Test protocol message creation."""
    message = ProtocolMessage(
        address=0x20,
        service_type=ServiceType.READ,
        command_class=CommandClass.CONTROL,
        instance=0x01,
        attribute=0x05
    )
    
    assert message.address == 0x20
    assert message.service_type == ServiceType.READ
    assert message.command_class == CommandClass.CONTROL


def test_exception_hierarchy():
    """Test that exceptions are properly organized."""
    assert issubclass(CommunicationError, SeverstarError)
    assert issubclass(CommunicationError, Exception)


def test_module_imports():
    """Test that all modules can be imported successfully."""
    # This test just ensures no import errors
    from severstar_mfc_rs485 import protocol
    from severstar_mfc_rs485 import communication
    from severstar_mfc_rs485 import commands
    from severstar_mfc_rs485 import exceptions
    
    assert protocol is not None
    assert communication is not None
    assert commands is not None
    assert exceptions is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
