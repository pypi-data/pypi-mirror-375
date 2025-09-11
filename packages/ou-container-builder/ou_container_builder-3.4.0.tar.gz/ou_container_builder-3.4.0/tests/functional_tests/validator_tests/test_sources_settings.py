"""Test the sources settings validation."""

from pydantic import ValidationError
from pytest import raises

from ou_container_builder.settings import AptDebLine, AptSource, Sources

from .util import error_locations


def test_valid_sources_settings():
    """Test that a valid sources configuration passes."""
    Sources(apt=[])


def test_default_sources_settings():
    """Test that the default sources settings are correct."""
    settings = Sources()
    assert settings.apt == []


def test_valid_apt_source_settings():
    """Test that a valid apt source configuration passes."""
    settings = AptSource(
        name="test",
        key_url="https://example.com/key-url",
        dearmor=False,
        deb={"url": "https://example.com/repo", "distribution": "test", "component": "main"},
    )
    assert settings.dearmor is False


def test_default_apt_source_settings():
    """Test that the default apt source settings are correct."""
    settings = AptSource(
        name="test",
        key_url="https://example.com/key-url",
        deb={"url": "https://example.com/repo", "distribution": "test", "component": "main"},
    )
    assert settings.dearmor is True


def test_invalid_apt_source_key_url_fails():
    """Test that an invalid key_url fails."""
    with raises(ValidationError) as e_info:
        AptSource(
            name="test",
            key_url="nowhere",
            deb={"url": "https://example.com/repo", "distribution": "test", "component": "main"},
        )
    assert ("key_url",) in error_locations(e_info.value)


def test_valid_apt_deb_line_settings():
    """Test that a valid apt source configuration passes."""
    AptDebLine(url="https://example.com/repo", distribution="test", component="main")


def test_invalid_apt_deb_line_url_fails():
    """Test that an invalid key_url fails."""
    with raises(ValidationError) as e_info:
        AptDebLine(url="nowhere", distribution="test", component="main")
    assert ("url",) in error_locations(e_info.value)
