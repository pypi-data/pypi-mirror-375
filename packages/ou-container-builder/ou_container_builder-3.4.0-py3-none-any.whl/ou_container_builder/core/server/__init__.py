"""Functionality for setting up the base server."""

import json
import os
from importlib.resources import files
from warnings import warn

from rich.progress import Progress

from ou_container_builder.state import State
from ou_container_builder.util import docker_copy_cmd, docker_run_cmd

CONTAINER_SCRIPT = """#!/bin/bash

mkdir -p $HOME
sudo /bin/chmod 775 $HOME

/var/lib/ou/python/system/bin/python /usr/share/ou/startup.py

if [[ ! -z "${JUPYTERHUB_API_TOKEN}" ]]; then
    export JUPYTERHUB_SINGLEUSER_APP='jupyter_server.serverapp.ServerApp'
    exec /var/lib/ou/python/system/bin/jupyterhub-singleuser
else
    exec /var/lib/ou/python/system/bin/jupyter server
fi
"""


def init(state: State) -> None:
    """Specify the base server configuration."""
    state.update(
        {
            "packages": {"pip": {"system": ["jupyter_server>=2.12,<3", "jupyterhub>=4.0.0,<5"]}},
            "jupyter_server_config": {
                "ServerApp": {
                    "ip": "0.0.0.0",  # noqa: S104
                    "port": 8888,
                    "trust_xheaders": True,
                },
                "ZMQChannelsWebsocketConnection": {"iopub_data_rate_limit": 10000000},
            },
        }
    )
    state.add_listener("server", server_listener)
    state.add_listener("module", server_listener)


def server_listener(state: State) -> None:
    """Update based on the server settings."""
    state.update({"jupyter_server_config": {"ServerApp": {"default_url": state["server"]["default_path"]}}})
    if state["server"]["access_token"] is not None:
        state.update({"jupyter_server_config": {"ServerApp": {"token": state["server"]["access_token"]}}})
    elif "module" in state and "code" in state["module"] and "presentation" in state["module"]:
        state.update(
            {
                "jupyter_server_config": {
                    "ServerApp": {"token": f"{state['module']['code']}-{state['module']['presentation']}".upper()}
                }
            }
        )
    if state["server"]["wrapper_host"] is not None:
        warn(
            "server.wrapper_host is deprected and will be removed with version 4",
            DeprecationWarning,
            stacklevel=2,
        )
        state.update(
            {
                "jupyter_server_config": {
                    "ServerApp": {
                        "tornado_settings": {
                            "headers": {
                                "Content-Security-Policy": f"frame-ancestors 'self' {state['server']['wrapper_host']}"
                            }
                        }
                    }
                }
            }
        )


def generate(state: State, progress: Progress) -> None:  # noqa: ARG001
    """Generate the blocks for the deploy stage."""
    os.makedirs(os.path.join("ou-builder-build", "server"), exist_ok=True)
    with open(os.path.join("ou-builder-build", "server", "vce-start.sh"), "w") as out_f:
        out_f.write(CONTAINER_SCRIPT)
    with open(os.path.join("ou-builder-build", "server", "jupyter_server_config.json"), "w") as out_f:
        json.dump(state["jupyter_server_config"], out_f)
    with open(os.path.join("ou-builder-build", "server", "startup.py"), "w") as out_f:
        out_f.write(files("ou_container_builder.core.server").joinpath("startup.py").read_text())
    with open(os.path.join("ou-builder-build", "server", "99-chmod-homedir"), "w") as out_f:
        out_f.write(
            f"{state['image']['user']} ALL=(root) NOPASSWD: /bin/chmod 775 /home/{state['image']['user']}/{state['module']['code']}-{state['module']['presentation']}\n"  # noqa: E501
        )
    state.update(
        {
            "output_blocks": {
                "deploy": [
                    {
                        "block": docker_copy_cmd(
                            os.path.join("ou-builder-build", "server", "vce-start.sh"),
                            "/usr/bin/vce-start.sh",
                        ),
                        "weight": 181,
                    },
                    {
                        "block": docker_copy_cmd(
                            os.path.join(
                                "ou-builder-build",
                                "server",
                                "jupyter_server_config.json",
                            ),
                            "/usr/local/etc/jupyter/jupyter_server_config.json",
                        ),
                        "weight": 181,
                    },
                    {
                        "block": docker_run_cmd(["chmod a+x /usr/bin/vce-start.sh"]),
                        "weight": 182,
                    },
                    {
                        "block": docker_copy_cmd(
                            os.path.join("ou-builder-build", "server", "startup.py"),
                            "/usr/share/ou/startup.py",
                        ),
                        "weight": 183,
                    },
                    {
                        "block": docker_copy_cmd(
                            os.path.join("ou-builder-build", "server", "99-chmod-homedir"),
                            "/etc/sudoers.d",
                        ),
                        "weight": 184,
                    },
                ]
            }
        }
    )
