"""Test the version command."""

from typer import Typer
from typer.testing import CliRunner

from ou_container_builder.__about__ import __version__


def test_current_version(runner: CliRunner, app: Typer):
    """Test that the current version is printed."""
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert result.stdout == f"{__version__}\n"
