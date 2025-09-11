"""Test the sources settings validation."""

from ou_container_builder.settings import WebApp


def test_valid_web_app_settings():
    """Test that a valid sources configuration passes."""
    WebApp(
        path="test",
        options={
            "command": ["python", "-m", "http.server", "{port}"],
            "port": 80,
            "timeout": 120,
            "absolute_url": True,
            "launcher_entry": {},
        },
    )
    WebApp(
        path="test",
        options={
            "command": "python -m http.server {port}",
            "port": 80,
            "timeout": 120,
            "absolute_url": True,
            "launcher_entry": {},
        },
    )


def test_default_web_app_settings():
    """Test that the default web_app settings are correct."""
    settings = WebApp(path="test", options={"command": ["python", "-m", "http.server", "{port}"]})
    assert settings.path == "test"
    assert settings.options["command"] == ["python", "-m", "http.server", "{port}"]
