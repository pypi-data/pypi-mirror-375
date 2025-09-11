"""CLI interface for building the container."""

import os
import shutil

from rich.progress import Progress

from ou_container_builder import core, packs
from ou_container_builder.cli.base import app
from ou_container_builder.settings import Settings, load_settings
from ou_container_builder.state import State


@app.command()
def generate():
    """Generate the Dockerfile."""
    with Progress() as progress:
        main_task = progress.add_task("Processing...", total=7)
        if os.path.exists("ou-builder-build"):
            shutil.rmtree("ou-builder-build")
        if os.path.exists("Dockerfile"):
            os.unlink("Dockerfile")
        os.makedirs("ou-builder-build")
        progress.update(main_task, advance=1)
        user_settings = load_settings()
        state = State()
        core.init(state, progress)
        packs.init(state, progress)
        progress.update(main_task, advance=1)
        progress.update(main_task, advance=1)
        state.update(user_settings)
        validated_settings = Settings(**state).model_dump()
        state = State()
        state.update(validated_settings)
        progress.update(main_task, advance=1)
        core.generate(state, progress)
        progress.update(main_task, advance=1)
        packs.generate(state, progress)
        progress.update(main_task, advance=1)
        with open("Dockerfile", "w") as out_f:
            blocks = state["output_blocks"]["build"]
            blocks.sort(key=lambda b: b["weight"])
            for block in blocks:
                out_f.write(block["block"])
                if block["block"].endswith("\n"):
                    out_f.write("\n")
                else:
                    out_f.write("\n\n")
            blocks = state["output_blocks"]["deploy"]
            blocks.sort(key=lambda b: b["weight"])
            for block in blocks:
                out_f.write(block["block"])
                if block["block"].endswith("\n"):
                    out_f.write("\n")
                else:
                    out_f.write("\n\n")
        progress.update(main_task, advance=1)
