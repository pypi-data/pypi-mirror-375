"""Functionality to install an IRkernel."""

import os

from pydantic import BaseModel
from rich.progress import Progress

from ou_container_builder.state import State
from ou_container_builder.util import docker_copy_cmd

name = "irkernel"
STARTUP_KERNEL_SCRIPT = """#!/bin/bash

PATH=$PATH:/var/lib/ou/python/system/bin/
R -e "IRkernel::installspec()"
"""


class Options(BaseModel):
    """Options for the irkernel pack."""

    pass


def init(state: State) -> None:
    """Initialise packs.irkernel."""
    state.update({"packages": {"apt": {"deploy": ["r-base", "r-cran-irkernel"]}}})


def generate(state: State, progress: Progress) -> None:  # noqa: ARG001
    """Generate the kernel installation script."""
    os.makedirs(os.path.join("ou-builder-build", "irkernel"), exist_ok=True)
    with open(os.path.join("ou-builder-build", "irkernel", "110-activating-the-R-kernel"), "w") as out_f:
        out_f.write(STARTUP_KERNEL_SCRIPT)
    state.update(
        {
            "output_blocks": {
                "deploy": [
                    {
                        "block": docker_copy_cmd(
                            os.path.join("ou-builder-build", "irkernel", "110-activating-the-R-kernel"),
                            "/usr/share/ou/startup.d/110-activating-the-R-kernel",
                        ),
                        "weight": 191,
                    }
                ]
            }
        }
    )
