"""Test the generate and clean functions."""

import os

from typer import Typer
from typer.testing import CliRunner


def test_generate_and_clean(runner: CliRunner, app: Typer):
    """Test that generating and cleaning succeeds."""
    cwd = os.getcwd()
    try:
        os.chdir(os.path.join("tests", "demos", "jupyterlab", "v4"))
        result = runner.invoke(app, ["clean"])
        assert not os.path.exists("Dockerfile")
        assert not os.path.exists("ou-builder-build")
        result = runner.invoke(app, ["clean"])
        assert result.exit_code == 0
        assert not os.path.exists("Dockerfile")
        assert not os.path.exists("ou-builder-build")
        result = runner.invoke(app, ["generate"])
        assert result.exit_code == 0
        assert os.path.exists("Dockerfile")
        assert os.path.exists("ou-builder-build")
        result = runner.invoke(app, ["generate"])
        assert result.exit_code == 0
        assert os.path.exists("Dockerfile")
        assert os.path.exists("ou-builder-build")
        result = runner.invoke(app, ["clean"])
        assert result.exit_code == 0
        assert not os.path.exists("Dockerfile")
        assert not os.path.exists("ou-builder-build")
    finally:
        os.chdir(cwd)
