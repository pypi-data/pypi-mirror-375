"""Functionality for setting up the user in both stages."""

from rich.progress import Progress

from ou_container_builder.state import State
from ou_container_builder.util import docker_run_cmd


def init(state: State) -> None:
    """Unused."""
    pass


def generate(state: State, progress: Progress) -> None:  # noqa: ARG001
    """Generate the user setup for the two stages."""
    state.update(
        {
            "output_blocks": {
                "build": [
                    {
                        "block": docker_run_cmd(
                            ["mkdir /home/$USER && useradd -u $UID -g $GID -d $HOME -m -s /bin/bash $USER"]
                        ),
                        "weight": 61,
                    }
                ],
                "deploy": [
                    {
                        "block": docker_run_cmd(
                            ["mkdir /home/$USER && useradd -u $UID -g $GID -d $HOME -m -s /bin/bash $USER"]
                        ),
                        "weight": 61,
                    }
                ],
            }
        }
    )
