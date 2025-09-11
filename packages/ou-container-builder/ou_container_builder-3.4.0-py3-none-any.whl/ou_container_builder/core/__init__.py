"""Core builder functionality."""

from rich.progress import Progress

from ou_container_builder.core import (
    apt,
    args,
    base,
    content,
    environment,
    python,
    rust,
    scripts,
    server,
    services,
    sources,
    user,
    webapp,
)
from ou_container_builder.state import State

CORE_PACKS = [apt, args, base, content, environment, python, rust, scripts, server, services, sources, user, webapp]


def init(state: State, progress: Progress) -> None:
    """Initialise all core packs."""
    core_task = progress.add_task("Initialising core...", total=len(CORE_PACKS))
    for pack in CORE_PACKS:
        pack.init(state)
        progress.update(core_task, advance=1)
    progress.update(core_task, visible=False)


def generate(state: State, progress: Progress) -> None:
    """Generate all files and Dockerfile snippets."""
    core_task = progress.add_task("Generating core...", total=len(CORE_PACKS))
    for pack in CORE_PACKS:
        pack.generate(state, progress)
        progress.update(core_task, advance=1)
    progress.update(core_task, visible=False)
