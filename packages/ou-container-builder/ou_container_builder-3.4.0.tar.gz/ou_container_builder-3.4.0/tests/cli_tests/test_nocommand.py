"""Test running without a command."""

from typer import Typer
from typer.testing import CliRunner


def test_no_command(runner: CliRunner, app: Typer):
    """Test that not providing a command fails."""
    result = runner.invoke(app)
    assert result.exit_code == 2
    assert "Usage:" in result.stderr


def test_empty_command(runner: CliRunner, app: Typer):
    """Test that providing an empty command list fails."""
    result = runner.invoke(app, [])
    assert result.exit_code == 2
    assert "Usage:" in result.stderr


def test_invalid_command(runner: CliRunner, app: Typer):
    """Test that providing an invalid command fails."""
    result = runner.invoke(app, ["not-exist"])
    assert result.exit_code == 2
    assert "Usage:" in result.stderr
