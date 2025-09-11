"""Functionality for setting up the base system."""

from rich.progress import Progress

from ou_container_builder.state import State


def init(state: State) -> None:
    """Specify the base packages to install."""
    state.update(
        {
            "packages": {
                "apt": {
                    "core": ["gcc", "build-essential"],
                    "build": [],
                    "deploy": [
                        "libcurl3-gnutls",
                        "libcurl3-gnutls-dev",
                        "gnutls-dev",
                        "sudo",
                        "tini",
                    ],
                },
                "pip": {"system": ["pycurl"], "user": ["pycurl"]},
            }
        }
    )


def generate(state: State, progress: Progress) -> None:  # noqa: ARG001
    """Generate the FROM blocks for the two stages."""
    state.update(
        {
            "output_blocks": {
                "build": [
                    {"block": "# ###########\n# Build Stage\n# ###########\n\n", "weight": 0},
                    {"block": f"FROM {state['image']['base']} as base", "weight": 1},
                    {"block": "USER root", "weight": 2},
                ],
                "deploy": [
                    {"block": "\n# ############\n# Deploy Stage\n# ############\n\n", "weight": 0},
                    {"block": f"FROM {state['image']['base']} as deploy", "weight": 1},
                    {"block": "USER root", "weight": 2},
                    {"block": "USER $USER\nWORKDIR $HOME\nEXPOSE 8888", "weight": 9001},
                    {"block": 'ENTRYPOINT ["tini", "-g", "--"]\nCMD ["/usr/bin/vce-start.sh"]', "weight": 9002},
                ],
            }
        }
    )
