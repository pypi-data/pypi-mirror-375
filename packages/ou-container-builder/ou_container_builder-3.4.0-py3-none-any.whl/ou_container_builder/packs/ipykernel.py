"""Functionality to install an iPython kernel."""

import os

from pydantic import BaseModel
from rich.progress import Progress

from ou_container_builder.state import State
from ou_container_builder.util import docker_copy_cmd, docker_run_cmd

name = "ipykernel"
STARTUP_KERNEL_SCRIPT = """#!/bin/bash

export PATH=$PATH:$HOME/.local/bin
ipython kernel install --name "Python-3" --user
"""


class Options(BaseModel):
    """Options for the ipykernel pack."""

    pass


def init(state: State) -> None:
    """Initialise packs.ipykernel."""
    state.update({"environment": [{"name": "PYDEVD_DISABLE_FILE_VALIDATION", "value": "1"}]})
    state.update({"packages": {"pip": {"user": ["ipykernel"]}}})


def generate(state: State, progress: Progress) -> None:  # noqa: ARG001
    """Uninstall the default kernel and activate the startup script."""
    os.makedirs(os.path.join("ou-builder-build", "ipykernel"), exist_ok=True)
    with open(
        os.path.join("ou-builder-build", "ipykernel", "110-activating-the-python-kernel"),
        "w",
    ) as out_f:
        out_f.write(STARTUP_KERNEL_SCRIPT)
    state.update(
        {
            "output_blocks": {
                "deploy": [
                    {
                        "block": docker_run_cmd(
                            [
                                "jupyter kernelspec remove -y python3",
                                "chown -f -R $USER:users $HOME/.ipython || true",
                                "chown -f -R $USER:users $HOME/.local || true",
                            ]
                        ),
                        "weight": 191,
                    },
                    {
                        "block": docker_copy_cmd(
                            os.path.join(
                                "ou-builder-build",
                                "ipykernel",
                                "110-activating-the-python-kernel",
                            ),
                            "/usr/share/ou/startup.d/110-activating-the-python-kernel",
                        ),
                        "weight": 192,
                    },
                ]
            }
        }
    )
