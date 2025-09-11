"""Test the image settings validation."""

from ou_container_builder.settings import Image


def test_valid_image_settings():
    """Test that a valid module configuration passes."""
    settings = Image(base="debian:stable", user="jovyan")
    assert settings.base == "debian:stable"
    assert settings.user == "jovyan"


def test_default_settings():
    """Test that the default settings are set correctly."""
    settings = Image()
    assert settings.base == "python:3.11-bookworm"
    assert settings.user == "ou"
