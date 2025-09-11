"""Functionality for setting up additional apt sources in both stages."""

import os
import shutil

from rich.progress import Progress

from ou_container_builder.state import State
from ou_container_builder.util import docker_copy_cmd


def init(state: State) -> None:
    """Add a services listener."""
    state.add_listener("services", services_listener)


def services_listener(state: State) -> None:
    """If services are configured, add required core packages."""
    if len(state["services"]) > 0:
        state.update({"packages": {"apt": {"deploy": ["sudo"]}}})


def generate(state: State, progress: Progress) -> None:  # noqa: ARG001
    """Generate the commands to start services."""
    if os.path.exists(os.path.join("ou-builder-build", "services")):
        shutil.rmtree(os.path.join("ou-builder-build", "services"))
    os.makedirs(os.path.join("ou-builder-build", "services", "sudoers"), exist_ok=True)
    os.makedirs(os.path.join("ou-builder-build", "services", "startup"), exist_ok=True)
    if len(state["services"]) > 0:
        for idx, service in enumerate(state["services"]):
            with open(os.path.join("ou-builder-build", "services", "sudoers", f"99-{service}"), "w") as out_f:
                out_f.write(
                    f"""{state["image"]["user"]} ALL=(root) NOPASSWD: /usr/sbin/service {service} start
{state["image"]["user"]} ALL=(root) NOPASSWD: /usr/sbin/service {service} restart
{state["image"]["user"]} ALL=(root) NOPASSWD: /usr/sbin/service {service} stop
"""
                )
            with open(
                os.path.join("ou-builder-build", "services", "startup", f"{50 + idx:03d}-starting-{service}"), "w"
            ) as out_f:
                out_f.write(
                    f"""#!/bin/bash

sudo /usr/sbin/service {service} start
"""
                )

        state.update(
            {
                "output_blocks": {
                    "deploy": [
                        {
                            "block": docker_copy_cmd(
                                os.path.join("ou-builder-build", "services", "sudoers"), "/etc/sudoers.d", chmod="0440"
                            ),
                            "weight": 311,
                        },
                        {
                            "block": docker_copy_cmd(
                                os.path.join("ou-builder-build", "services", "startup"), "/usr/share/ou/startup.d"
                            ),
                            "weight": 311,
                        },
                    ]
                }
            }
        )
