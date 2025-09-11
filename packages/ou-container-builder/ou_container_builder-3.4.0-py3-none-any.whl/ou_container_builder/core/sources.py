"""Functionality for setting up additional apt sources in both stages."""

from rich.progress import Progress

from ou_container_builder.state import State
from ou_container_builder.util import docker_run_cmd


def init(state: State) -> None:
    """Unused."""
    state.add_listener("sources.apt", apt_sources_listener)


def apt_sources_listener(state: State) -> None:
    """If additional sources are configured, add required core packages."""
    if len(state["sources"]["apt"]) > 0:
        state.update({"packages": {"apt": {"core": ["gnupg"]}}})


def generate(state: State, progress: Progress) -> None:  # noqa: ARG001
    """Generate the commands to download signing keys and create source list files."""
    if len(state["sources"]["apt"]) > 0:
        commands = []
        for source in state["sources"]["apt"]:
            if source["dearmor"]:
                commands.append(
                    f'curl -fsSL "{source["key_url"]}" | gpg --dearmor -o "/usr/share/keyrings/{source["name"]}.gpg"'
                )
            else:
                commands.append(f'curl -fsSL "{source["key_url"]}" > "/usr/share/keyrings/{source["name"]}.gpg"')
            commands.append(
                f'echo "deb [signed-by=/usr/share/keyrings/{source["name"]}.gpg] {source["deb"]["url"]} {source["deb"]["distribution"]} {source["deb"]["component"]}" > "/etc/apt/sources.list.d/{source["name"]}.list"'  # noqa: E501
            )
        state.update(
            {
                "output_blocks": {
                    "build": [
                        {
                            "block": docker_run_cmd(commands),
                            "weight": 121,
                        }
                    ],
                    "deploy": [
                        {
                            "block": docker_run_cmd(commands),
                            "weight": 121,
                        }
                    ],
                }
            }
        )
