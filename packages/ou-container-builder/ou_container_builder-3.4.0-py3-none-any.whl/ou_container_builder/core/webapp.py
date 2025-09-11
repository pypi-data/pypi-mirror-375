"""Functionality for setting up the user in both stages."""

from rich.progress import Progress

from ou_container_builder.state import State


def init(state: State) -> None:
    """Add a listener for the web_apps key."""
    state.add_listener("web_apps", activate_webapps)


def activate_webapps(state: State) -> None:
    """Activate the jupyter-server-proxy and set the config."""
    if len(state["web_apps"]) > 0:
        state.update({"packages": {"pip": {"system": ["jupyter-server-proxy>=4.1.0,<5"]}}})
        state.update(
            {
                "jupyter_server_config": {
                    "ServerProxy": {"servers": {web_app["path"]: web_app["options"] for web_app in state["web_apps"]}}
                }
            }
        )


def generate(state: State, progress: Progress) -> None:
    """Unused."""
    pass
