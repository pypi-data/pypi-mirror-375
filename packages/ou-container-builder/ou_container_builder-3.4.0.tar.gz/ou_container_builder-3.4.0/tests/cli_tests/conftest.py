"""Fixtures for the CLI tests."""

from pytest import fixture
from typer import Typer
from typer.testing import CliRunner

from ou_container_builder.__main__ import app as cli_app

collect_ignore = ["test_build.py"]


@fixture()
def runner() -> CliRunner:
    """Provide a CliRunner as a fixture."""
    return CliRunner()


@fixture
def app() -> Typer:
    """Provide the Typer application as a fixture."""
    return cli_app
