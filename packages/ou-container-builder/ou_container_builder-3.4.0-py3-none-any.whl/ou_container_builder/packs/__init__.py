"""Extension packs."""

from collections.abc import Callable
from importlib import import_module
from importlib.metadata import entry_points
from typing import Any

from rich.progress import Progress

from ou_container_builder.state import State

EXTENSION_PACKS = {}
for entry_point in entry_points().select(group="ou_container_builder"):
    EXTENSION_PACKS[entry_point.name] = import_module(entry_point.value)


def make_listener(key: str, pack: Any) -> Callable[[State], None]:
    """Create a custom listener for the key and pack."""

    def listener(listener_state: State) -> None:
        if key in listener_state["packs"] and listener_state["packs"][key] is not None:
            pack.init(listener_state)

    return listener


def init(state: State, progress: Progress) -> None:
    """Initialise all extension packs."""
    extension_task = progress.add_task("Initialising packs...", total=len(EXTENSION_PACKS))
    for key, pack in EXTENSION_PACKS.items():
        state.add_listener(f"packs.{key}", make_listener(key, pack))
        progress.update(extension_task, advance=1)
    progress.update(extension_task, visible=False)


def generate(state: State, progress: Progress) -> None:
    """Generate all files and Dockerfile snippets."""
    extension_task = progress.add_task("Generating packs...", total=len(EXTENSION_PACKS))
    for key, pack in EXTENSION_PACKS.items():
        if key in state["packs"] and state["packs"][key] is not None:
            pack.generate(state, progress)
        progress.update(extension_task, advance=1)
    progress.update(extension_task, visible=False)
