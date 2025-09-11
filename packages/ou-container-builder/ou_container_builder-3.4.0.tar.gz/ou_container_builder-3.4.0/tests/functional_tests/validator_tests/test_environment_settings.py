"""Test the environment settings validation."""

from pydantic import ValidationError
from pytest import raises

from ou_container_builder.settings import EnvironmentVariable

from .util import error_locations


def test_valid_environment_settings():
    """Test that a valid environment configuration passes."""
    EnvironmentVariable(name="EXTRA", value="yes")


def test_empty_name_fails():
    """Test that an environment variable with an empty name fails."""
    with raises(ValidationError) as e_info:
        EnvironmentVariable(name="", value="")
    assert ("name",) in error_locations(e_info.value)


def test_null_value_fails():
    """Test that an environment variable with a None value fails."""
    with raises(ValidationError) as e_info:
        EnvironmentVariable(name="TEST", value=None)
    assert ("value",) in error_locations(e_info.value)
