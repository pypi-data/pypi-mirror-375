"""Test the server settings validation."""

from ou_container_builder.settings import Server


def test_default_server_settings():
    """Test that the default server configuration passes."""
    settings = Server()
    assert settings.default_path == "/"
    assert settings.access_token is None
    assert settings.wrapper_host == "*.open.ac.uk"


def test_valid_server_settings():
    """Test that a valid server configuration passes."""
    settings = Server(default_path="/lab", access_token="test", wrapper_host="*.dev.open.ac.uk")
    assert settings.default_path == "/lab"
    assert settings.access_token == "test"
    assert settings.wrapper_host == "*.dev.open.ac.uk"
