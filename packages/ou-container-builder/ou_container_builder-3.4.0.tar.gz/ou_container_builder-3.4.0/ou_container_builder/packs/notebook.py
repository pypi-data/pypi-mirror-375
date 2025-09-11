"""Functionality to install Notebook."""

from typing import Literal

from pydantic import BaseModel
from rich.progress import Progress

from ou_container_builder.state import State

name = "notebook"


class Options(BaseModel):
    """Options for the Notebook pack."""

    version: Literal[7] = 7


def init(state: State) -> None:
    """Initialise packs.notebook."""
    if state["packs"]["notebook"]["version"] == 7:  # noqa: PLR2004
        state.update({"packages": {"pip": {"system": ["notebook>=7.1.1,<8"]}}})


def generate(state: State, progress: Progress) -> None:
    """Unused."""
    pass
