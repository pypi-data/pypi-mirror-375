"""Build function."""

import subprocess
from typing import Annotated

import typer

from ou_container_builder.cli.base import app
from ou_container_builder.cli.clean import clean
from ou_container_builder.cli.generate import generate


@app.command()
def build(
    tag: Annotated[list[str] | None, typer.Option(help="Docker tags to use")] = None,
    cache: Annotated[bool, typer.Option(help="Cache intermediate layers (true)")] = True,  # noqa: FBT002
) -> None:
    """Build the container image."""
    generate()
    cmd = ["buildah", "build", "--jobs", "2"]
    if tag is not None:
        for t in tag:
            cmd.extend(["--tag", t])
    if cache:
        cmd.extend(["--layers"])
    cmd.append(".")
    process = subprocess.run(cmd, check=False)  # noqa: S603
    if process.returncode == 0:
        clean()
