"""Test the content settings validation."""

from pydantic import ValidationError
from pytest import raises

from ou_container_builder.settings import Content


def test_valid_content_settings():
    """Test that a valid content configurations pass."""
    Content(source="test", target="/var/lib/test", overwrite="always")
    Content(source="test", target="/var/lib/test", overwrite="never")


def test_default_settings():
    """Test that the default settings are set correctly."""
    settings = Content(source="test", overwrite="always")
    assert settings.target == ""


def test_invalid_overwrite_mode():
    """Test that an invalid overwrite setting fails."""
    with raises(ValidationError):
        Content(source="test", overwrite="sometimes")
