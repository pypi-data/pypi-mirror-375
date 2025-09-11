"""Functionality for running scripts in the build and live phase."""

# TODO: Validation tests needed
import os
import shutil

from rich.progress import Progress

from ou_container_builder.state import State
from ou_container_builder.util import docker_copy_cmd, docker_run_cmd

SCRIPT_BASE_WEIGHT = 211


def init(state: State) -> None:
    """Unused."""
    pass


def generate(state: State, progress: Progress) -> None:
    """Generate the FROM blocks for the two stages."""
    if os.path.exists(os.path.join("ou-builder-build", "scripts")):
        shutil.rmtree(os.path.join("ou-builder-build", "scripts"))
    os.makedirs(os.path.join("ou-builder-build", "scripts", "startup"), exist_ok=True)
    os.makedirs(os.path.join("ou-builder-build", "scripts", "shutdown"), exist_ok=True)
    task = progress.add_task("Generating custom scripts", total=len(state["scripts"]))
    for idx, script in enumerate(state["scripts"]):
        if script["stage"] == "build":
            state.update(
                {
                    "output_blocks": {
                        "build": [
                            {
                                "block": docker_run_cmd(script["commands"]),
                                "weight": 201 + idx,
                            }
                        ]
                    }
                }
            )
        elif script["stage"] == "deploy":
            state.update(
                {
                    "output_blocks": {
                        "deploy": [
                            {
                                "block": docker_run_cmd(script["commands"]),
                                "weight": 201 + idx,
                            }
                        ]
                    }
                }
            )
        elif script["stage"] == "startup":
            if not script["commands"][0].startswith("#!"):
                script["commands"].insert(0, "#!/bin/bash")
            filename = f"{script['name'].lower().replace(' ', '-')}"
            with open(os.path.join("ou-builder-build", "scripts", "startup", filename), "w") as out_f:
                for line in script["commands"]:
                    out_f.write(line)
                    out_f.write("\n")
            state.update(
                {
                    "output_blocks": {
                        "deploy": [
                            {
                                "block": docker_copy_cmd(
                                    os.path.join(
                                        "ou-builder-build",
                                        "scripts",
                                        "startup",
                                        filename,
                                    ),
                                    f"/usr/share/ou/startup.d/{filename}",
                                ),
                                "weight": SCRIPT_BASE_WEIGHT + idx,
                            }
                        ]
                    }
                }
            )
        progress.update(task, advance=1)
    progress.update(task, visible=False)
