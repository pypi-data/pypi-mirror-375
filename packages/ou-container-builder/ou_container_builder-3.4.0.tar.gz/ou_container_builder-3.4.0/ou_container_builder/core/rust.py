"""Functionality for setting up rust in the build stage."""

from rich.progress import Progress

from ou_container_builder.state import State
from ou_container_builder.util import docker_run_cmd


def init(state: State) -> None:
    """Specify the base packages to install."""
    state.update({"packages": {"apt": {"core": ["curl"]}}})


def generate(state: State, progress: Progress) -> None:  # noqa: ARG001
    """Generate the FROM blocks for the two stages."""
    state.update(
        {
            "output_blocks": {
                "build": [
                    {
                        "block": docker_run_cmd(
                            ["curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y"]
                        ),
                        "weight": 101,
                    },
                ],
            }
        }
    )
