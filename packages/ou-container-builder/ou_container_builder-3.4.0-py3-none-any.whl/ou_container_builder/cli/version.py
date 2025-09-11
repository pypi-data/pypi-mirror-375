"""Version CLI command."""

from ou_container_builder.__about__ import __version__
from ou_container_builder.cli.base import app


@app.command()
def version():
    """Print the installed version."""
    print(__version__)  # noqa: T201
