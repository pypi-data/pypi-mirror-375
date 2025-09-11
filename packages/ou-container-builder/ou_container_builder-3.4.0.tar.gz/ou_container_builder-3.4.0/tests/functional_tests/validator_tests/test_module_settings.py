"""Test the module settings validation."""

from pydantic import ValidationError
from pytest import raises

from ou_container_builder.settings import Module

from .util import error_locations


def test_valid_module_settings():
    """Test that a valid module configuration passes."""
    Module(code="TEST001", presentation="23J")


def test_missing_module_code():
    """Test that a module configuration without a code fails."""
    with raises(ValidationError) as e_info:
        Module(presentation="23J")
    assert ("code",) in error_locations(e_info.value)


def test_missing_module_presentation():
    """Test that a module configuration without a presentation fails."""
    with raises(ValidationError) as e_info:
        Module(code="TEST001")
    assert ("presentation",) in error_locations(e_info.value)
