"""Functionality for setting up the system environment variables."""

from rich.progress import Progress

from ou_container_builder.state import State


def init(state: State) -> None:
    """Set the default environments."""
    state.update(
        {
            "environment": [
                {"name": "USER", "value": None},
                {"name": "UID", "value": "1000"},
                {"name": "GID", "value": "100"},
                {"name": "MODULE_CODE", "value": None},
                {"name": "MODULE_PRESENTATION", "value": None},
                {"name": "HOME", "value": "/home/$USER/$MODULE_CODE-$MODULE_PRESENTATION"},
                {"name": "SHELL", "value": "/bin/bash"},
                {"name": "PATH", "value": "$HOME/.local/bin:$PATH"},
            ]
        }
    )
    state.add_listener("image.user", update_environment)
    state.add_listener("module.code", update_environment)
    state.add_listener("module.presentation", update_environment)


def update_environment(state: State):
    """Update the environment setting based on the image and module states."""
    for env in state["environment"]:
        if env["name"] == "USER" and "image" in state and "user" in state["image"]:
            env["value"] = state["image"]["user"]
        elif env["name"] == "MODULE_CODE" and "module" in state and "code" in state["module"]:
            env["value"] = state["module"]["code"]
        elif env["name"] == "MODULE_PRESENTATION" and "module" in state and "presentation" in state["module"]:
            env["value"] = state["module"]["presentation"]


def generate(state: State, progress: Progress) -> None:  # noqa: ARG001
    """Generate the ENV blocks for the two stages."""
    state.update(
        {
            "output_blocks": {
                "build": [
                    {
                        "block": "\n".join(f'ENV {env["name"]}="{env["value"]}"' for env in state["environment"]),
                        "weight": 41,
                    }
                ],
                "deploy": [
                    {
                        "block": "\n".join(f'ENV {env["name"]}="{env["value"]}"' for env in state["environment"]),
                        "weight": 41,
                    }
                ],
            }
        }
    )
