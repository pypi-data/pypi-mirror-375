"""Functionality for setting up the build arguments."""

from rich.progress import Progress

from ou_container_builder.state import State


def init(state: State) -> None:
    """Set the default ARGs."""
    state.update({"args": []})


def generate(state: State, progress: Progress) -> None:  # noqa: ARG001
    """Generate the ARG blocks for the two stages."""
    state.update(
        {
            "output_blocks": {
                "build": [
                    {
                        "block": "\n".join(
                            f'ARG {arg["name"]}="{arg["value"]}"' if arg["value"] is not None else f"ARG {arg['name']}"
                            for arg in state["args"]
                        ),
                        "weight": 21,
                    }
                ],
                "deploy": [
                    {
                        "block": "\n".join(
                            f'ARG {arg["name"]}="{arg["value"]}"' if arg["value"] is not None else f"ARG {arg['name']}"
                            for arg in state["args"]
                        ),
                        "weight": 21,
                    }
                ],
            }
        }
    )
