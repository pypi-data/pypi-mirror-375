"""Clean-up function."""

import os
import shutil

from ou_container_builder.cli.base import app


@app.command()
def clean():
    """Clean the build files."""
    if os.path.exists("ou-builder-build"):
        shutil.rmtree("ou-builder-build")
    if os.path.exists("Dockerfile"):
        os.unlink("Dockerfile")
