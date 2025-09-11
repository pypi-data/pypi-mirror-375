"""Test that the builder works."""

import os
import subprocess

from typer import Typer
from typer.testing import CliRunner


def test_build_code_server(runner: CliRunner, app: Typer):
    """Test that building the code-server demo works."""
    cwd = os.getcwd()
    try:
        os.chdir(os.path.join("tests", "demos", "code_server"))
        result = runner.invoke(app, ["clean"])
        assert not os.path.exists("Dockerfile")
        assert not os.path.exists("ou-builder-build")
        result = runner.invoke(app, ["build", "--tag", "code_server:test"])
        assert result.exit_code == 0
        assert not os.path.exists("Dockerfile")
        assert not os.path.exists("ou-builder-build")
    finally:
        os.chdir(cwd)
        subprocess.run(["buildah", "rmi", "code_server:test"], check=False)  # noqa: S607


def test_build_jupyterlab_v3(runner: CliRunner, app: Typer):
    """Test that building the JupyterLab v3 demo works."""
    cwd = os.getcwd()
    try:
        os.chdir(os.path.join("tests", "demos", "jupyterlab", "v3"))
        result = runner.invoke(app, ["clean"])
        assert not os.path.exists("Dockerfile")
        assert not os.path.exists("ou-builder-build")
        result = runner.invoke(app, ["build", "--tag", "jupyterlab_v3:test"])
        assert result.exit_code == 0
        assert not os.path.exists("Dockerfile")
        assert not os.path.exists("ou-builder-build")
    finally:
        os.chdir(cwd)
        subprocess.run(["buildah", "rmi", "jupyterlab_v3:test"], check=False)  # noqa: S607


def test_build_jupyterlab_v4(runner: CliRunner, app: Typer):
    """Test that building the JupyterLab v4 demo works."""
    cwd = os.getcwd()
    try:
        os.chdir(os.path.join("tests", "demos", "jupyterlab", "v4"))
        result = runner.invoke(app, ["clean"])
        assert not os.path.exists("Dockerfile")
        assert not os.path.exists("ou-builder-build")
        result = runner.invoke(app, ["build", "--tag", "jupyterlab_v4:test"])
        assert result.exit_code == 0
        assert not os.path.exists("Dockerfile")
        assert not os.path.exists("ou-builder-build")
    finally:
        os.chdir(cwd)
        subprocess.run(["buildah", "rmi", "jupyterlab_v4:test"], check=False)  # noqa: S607


def test_build_custom_apt_key_dearmor(runner: CliRunner, app: Typer):
    """Test that building the custom_apt_key_dearmor demo works."""
    cwd = os.getcwd()
    try:
        os.chdir(os.path.join("tests", "demos", "custom_apt_key_dearmor"))
        result = runner.invoke(app, ["clean"])
        assert not os.path.exists("Dockerfile")
        assert not os.path.exists("ou-builder-build")
        result = runner.invoke(app, ["build", "--tag", "custom_apt_key_dearmor:test"])
        assert result.exit_code == 0
        assert not os.path.exists("Dockerfile")
        assert not os.path.exists("ou-builder-build")
    finally:
        os.chdir(cwd)
        subprocess.run(["buildah", "rmi", "custom_apt_key_dearmor:test"], check=False)  # noqa: S607


def test_build_openrefine(runner: CliRunner, app: Typer):
    """Test that building the openrefine demo works."""
    cwd = os.getcwd()
    try:
        os.chdir(os.path.join("tests", "demos", "openrefine"))
        result = runner.invoke(app, ["clean"])
        assert not os.path.exists("Dockerfile")
        assert not os.path.exists("ou-builder-build")
        result = runner.invoke(app, ["build", "--tag", "openrefine:test"])
        assert result.exit_code == 0
        assert not os.path.exists("Dockerfile")
        assert not os.path.exists("ou-builder-build")
    finally:
        os.chdir(cwd)
        subprocess.run(["buildah", "rmi", "openrefine:test"], check=False)  # noqa: S607
