"""Functionality to handle installing apt packages."""

from rich.progress import Progress

from ou_container_builder.state import State
from ou_container_builder.util import docker_run_cmd


def init(state: State) -> None:
    """Unused."""
    pass


def generate(state: State, progress: Progress) -> None:  # noqa: ARG001
    """Generate the blocks to install all apt packages in the build and deploy stages."""
    state.update(
        {
            "output_blocks": {
                "build": [
                    {
                        "block": docker_run_cmd(
                            [
                                "DEBIAN_FRONTEND=noninteractive apt-get update -y",
                                "DEBIAN_FRONTEND=noninteractive apt-get dist-upgrade -y",
                                f"DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends {' '.join(state['packages']['apt']['core'])}",  # noqa: E501
                            ]
                        ),
                        "weight": 91,
                    },
                ],
                "deploy": [
                    {
                        "block": docker_run_cmd(
                            [
                                "DEBIAN_FRONTEND=noninteractive apt-get update -y",
                                "DEBIAN_FRONTEND=noninteractive apt-get dist-upgrade -y",
                                f"DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends {' '.join(state['packages']['apt']['core'])}",  # noqa: E501
                            ]
                        ),
                        "weight": 91,
                    },
                ],
            }
        }
    )
    if len(state["packages"]["apt"]["build"]) > 0:
        state.update(
            {
                "output_blocks": {
                    "build": [
                        {
                            "block": docker_run_cmd(
                                [
                                    "DEBIAN_FRONTEND=noninteractive apt-get update -y",
                                    "DEBIAN_FRONTEND=noninteractive apt-get dist-upgrade -y",
                                    f"DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends {' '.join(state['packages']['apt']['build'])}",  # noqa: E501
                                ]
                            ),
                            "weight": 141,
                        },
                    ],
                }
            }
        )
    if len(state["packages"]["apt"]["deploy"]) > 0:
        state.update(
            {
                "output_blocks": {
                    "deploy": [
                        {
                            "block": docker_run_cmd(
                                [
                                    "DEBIAN_FRONTEND=noninteractive apt-get update -y",
                                    "DEBIAN_FRONTEND=noninteractive apt-get dist-upgrade -y",
                                    f"DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends {' '.join(state['packages']['apt']['deploy'])}",  # noqa: E501
                                ]
                            ),
                            "weight": 141,
                        },
                    ],
                }
            }
        )
