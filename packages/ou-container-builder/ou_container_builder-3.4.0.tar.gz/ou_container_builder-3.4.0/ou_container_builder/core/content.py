"""Functionality for copying content into the image."""

import os
import shutil
import subprocess

from rich.progress import Progress

from ou_container_builder.state import State
from ou_container_builder.util import docker_copy_cmd


def init(state: State) -> None:
    """Unused."""
    pass


def generate(state: State, progress: Progress) -> None:
    """Copy the content files."""
    content_task = progress.add_task("Compressing content to distribute...", target=len(state["content"]))
    os.makedirs(os.path.join("ou-builder-build", "content", "archives"), exist_ok=True)
    unpack_commands = []
    for idx, content in enumerate(state["content"]):
        if content["target"].startswith("/"):
            state.update(
                {
                    "output_blocks": {
                        "deploy": [{"block": docker_copy_cmd(content["source"], content["target"]), "weight": 181}]
                    }
                }
            )
        else:
            if content["source"].endswith("/"):
                content["source"] = content["source"][:-1]
            if os.path.isfile(content["source"]):
                shutil.copyfile(
                    content["source"], os.path.join("ou-builder-build", "content", "archives", f"content-{idx}")
                )
                unpack_commands.append(f"cp /usr/share/ou/content/content-{idx} $HOME/{content['target']}")
            else:
                basepath, itemname = os.path.split(content["source"])
                if basepath:
                    subprocess.run(  # noqa: S603
                        [  # noqa: S607
                            "tar",
                            "-jcf",
                            os.path.join("ou-builder-build", "content", "archives", f"content-{idx}.tar.bz2"),
                            "--directory",
                            basepath,
                            itemname,
                        ],
                        check=False,
                    )
                else:
                    subprocess.run(  # noqa: S603
                        [  # noqa: S607
                            "tar",
                            "-jcf",
                            os.path.join("ou-builder-build", "content", "archives", f"content-{idx}.tar.bz2"),
                            itemname,
                        ],
                        check=False,
                    )
                unpack_commands.append(f"mkdir -p $HOME/{content['target']}")
                if content["overwrite"] == "always":
                    unpack_commands.append(
                        f"tar -jxf /usr/share/ou/content/content-{idx}.tar.bz2 --directory $HOME/{content['target']} --strip-components=1"  # noqa: E501
                    )
                elif content["overwrite"] == "never":
                    unpack_commands.append(
                        f"tar -jxf /usr/share/ou/content/content-{idx}.tar.bz2 --skip-old-files --directory $HOME/{content['target']} --strip-components=1"  # noqa: E501
                    )
        progress.update(content_task, advance=1)
    if len(unpack_commands) > 0:
        with open(os.path.join("ou-builder-build", "content", "020-distributing-files"), "w") as out_f:
            unpack_commmand_text = "\n".join(unpack_commands)
            out_f.write(
                f"""#!/bin/bash
{unpack_commmand_text}"""
            )
        state.update(
            {
                "output_blocks": {
                    "deploy": [
                        {
                            "block": docker_copy_cmd(
                                os.path.join("ou-builder-build", "content", "archives"), "/usr/share/ou/content"
                            ),
                            "weight": 182,
                        },
                        {
                            "block": docker_copy_cmd(
                                os.path.join("ou-builder-build", "content", "020-distributing-files"),
                                "/usr/share/ou/startup.d/020-distributing-files",
                            ),
                            "weight": 183,
                        },
                    ]
                }
            }
        )
    progress.update(content_task, visible=False)
