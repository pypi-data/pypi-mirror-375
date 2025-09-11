"""Test the docker args settings validation."""

from ou_container_builder.settings import Arg


def test_valid_docker_args_settings():
    """Test that a valid docker args configuration passes."""
    Arg(name="TARGETPLATFORM")
    Arg(name="TARGETPLATFORM", value="linux/amd64")
