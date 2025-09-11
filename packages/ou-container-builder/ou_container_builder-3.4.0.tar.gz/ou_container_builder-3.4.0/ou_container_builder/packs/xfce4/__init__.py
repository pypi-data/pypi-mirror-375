"""Functionality to install XFCE4 virtual desktop."""

import os
import shutil
from importlib.resources import open_binary, open_text

from pydantic import BaseModel
from rich.progress import Progress

from ou_container_builder.state import State
from ou_container_builder.util import docker_copy_cmd, docker_run_cmd

name = "xfce4"


class Options(BaseModel):
    """Options for the XFCE4 pack."""

    pass


def init(state: State) -> None:
    """Initialise packs.jupyterlab."""
    if os.path.exists(os.path.join("ou-builder-build", "xfce4", "xfce4", "xfconf", "xfce-perchannel-xml")):
        shutil.rmtree(os.path.join("ou-builder-build", "xfce4", "xfce4", "xfconf", "xfce-perchannel-xml"))
    os.makedirs(os.path.join("ou-builder-build", "xfce4", "xfce4", "xfconf", "xfce-perchannel-xml"), exist_ok=True)
    with open(
        os.path.join("ou-builder-build", "xfce4", "xfce4", "xfconf", "xfce-perchannel-xml", "xfce4-desktop.xml"), "w"
    ) as out_f:
        with open_text("ou_container_builder.packs.xfce4", "xfce4-desktop.xml") as in_f:
            out_f.write(in_f.read())
    with open(
        os.path.join("ou-builder-build", "xfce4", "xfce4", "xfconf", "xfce-perchannel-xml", "xfwm4.xml"), "w"
    ) as out_f:
        with open_text("ou_container_builder.packs.xfce4", "xfwm4.xml") as in_f:
            out_f.write(in_f.read())
    with open(os.path.join("ou-builder-build", "xfce4", "desktop.jpg"), "wb") as out_f:
        with open_binary("ou_container_builder.packs.xfce4", "desktop.jpg") as in_f:
            out_f.write(in_f.read())
    state.update(
        {
            "packages": {
                "apt": {
                    "deploy": [
                        "dbus-x11",
                        "libgl1-mesa-glx",
                        "xorg",
                        "xfce4",
                        "xfce4-panel",
                        "xfce4-session",
                        "xfce4-settings",
                        "at-spi2-core",
                        "tigervnc-standalone-server",
                        "viewnior",
                        "firefox-esr",
                    ]
                },
                "pip": {"system": ["jupyter-remote-desktop-proxy", "git+https://github.com/novnc/websockify.git"]},
            },
            "content": [
                {
                    "source": os.path.join("ou-builder-build", "xfce4", "xfce4"),
                    "target": ".config/xfce4",
                    "overwrite": "always",
                }
            ],
        }
    )


def generate(state: State, progress: Progress) -> None:  # noqa: ARG001
    """Generate the files to distribute and the Docker blocks."""
    state.update(
        {
            "output_blocks": {
                "build": [
                    {
                        "block": docker_run_cmd(
                            [
                                "git clone https://github.com/novnc/websockify.git /tmp/websockify",
                                "cd /tmp/websockify",
                                "make",
                            ]
                        ),
                        "weight": 1021,
                    }
                ],
                "deploy": [
                    {
                        "block": docker_run_cmd(
                            ["ln -s /var/lib/ou/python/system/bin/websockify /usr/local/bin/websockify"]
                        ),
                        "weight": 1021,
                    },
                    {
                        "block": docker_copy_cmd(
                            "/tmp/websockify/rebind.so",  # noqa: S108
                            "/usr/local/bin/rebind.so",
                            from_stage="base",
                        ),
                        "weight": 1022,
                    },
                    {
                        "block": docker_copy_cmd(
                            "ou-builder-build/xfce4/desktop.jpg", "/usr/share/backgrounds/xfce/open-university.jpg"
                        ),
                        "weight": 1023,
                    },
                ],
            }
        }
    )
