"""Functionality for installing python packages.

The packages are downloaded and built in the build stage and then the wheels are copied over into the
deploy stage. The system packages are then installed into a venv at /var/lib/ou/python/system.

Packages are installed from requirements files. If package names are provided directly, then a requirements.txt
is generated for those.
"""

from rich.progress import Progress

from ou_container_builder.state import State
from ou_container_builder.util import docker_copy_cmd, docker_run_cmd


def init(state: State) -> None:
    """Unused."""
    pass


def generate(state: State, progress: Progress) -> None:  # noqa: ARG001
    """Generate the python wheel build and install blocks."""
    # If there are any installed packages copy them from the build to the deploy stage
    if len(state["packages"]["pip"]["system"]) > 0 or len(state["packages"]["pip"]["user"]) > 0:
        state.update(
            {
                "output_blocks": {
                    "deploy": [
                        {
                            "block": docker_copy_cmd("/usr/share/ou/python", "/usr/share/ou/python", from_stage="base"),
                            "weight": 161,
                        },
                    ]
                }
            }
        )
    # Install any system python packages
    if len(state["packages"]["pip"]["system"]) > 0:
        system_packages = "\\n".join(
            [pkg["name"] for pkg in state["packages"]["pip"]["system"] if pkg["type"] == "package"]
        )
        requirement_files = " ".join(
            [
                f"-r /usr/share/ou/python/system/requirements-{idx + 1}.txt"
                for idx, pkg in enumerate(state["packages"]["pip"]["system"])
                if pkg["type"] == "requirements.txt"
            ]
        )
        state.update(
            {
                "output_blocks": {
                    "build": [
                        {
                            "block": docker_copy_cmd(
                                pkg["name"], f"/usr/share/ou/python/system/requirements-{idx + 1}.txt"
                            ),
                            "weight": 161,
                        }
                        for idx, pkg in enumerate(state["packages"]["pip"]["system"])
                        if pkg["type"] == "requirements.txt"
                    ]
                }
            }
        )
        state.update(
            {
                "output_blocks": {
                    "build": [
                        {
                            "block": docker_run_cmd(
                                [
                                    "mkdir -p /usr/share/ou/python/system",
                                    f'echo "{system_packages}" > /usr/share/ou/python/system/requirements-0.txt',
                                ]
                            ),
                            "weight": 161,
                        },
                        {
                            "block": docker_run_cmd(
                                [
                                    f"pip wheel --no-cache-dir -w /usr/share/ou/python/system -r /usr/share/ou/python/system/requirements-0.txt {requirement_files}",  # noqa: E501
                                ]
                            ),
                            "weight": 162,
                        },
                    ],
                    "deploy": [
                        {
                            "block": docker_run_cmd(
                                [
                                    "mkdir -p /var/lib/ou/python",
                                    "python -m venv /var/lib/ou/python/system",
                                    "/var/lib/ou/python/system/bin/pip install --no-index --no-deps /usr/share/ou/python/system/*.whl",  # noqa: E501
                                    "/var/lib/ou/python/system/bin/pip uninstall -y ipykernel",
                                ]
                            ),
                            "weight": 162,
                        },
                    ],
                }
            }
        )
    # Build any user packages
    if len(state["packages"]["pip"]["user"]) > 0:
        user_packages = "\\n".join(
            [pkg["name"] for pkg in state["packages"]["pip"]["user"] if pkg["type"] == "package"]
        )
        # Build and copy the requirements files
        requirement_files = " ".join(
            [
                f"-r /usr/share/ou/python/user/requirements-{idx + 1}.txt"
                for idx, pkg in enumerate(state["packages"]["pip"]["user"])
                if pkg["type"] == "requirements.txt"
            ]
        )
        state.update(
            {
                "output_blocks": {
                    "build": [
                        {
                            "block": docker_copy_cmd(
                                pkg["name"], f"/usr/share/ou/python/user/requirements-{idx + 1}.txt"
                            ),
                            "weight": 163,
                        }
                        for idx, pkg in enumerate(state["packages"]["pip"]["user"])
                        if pkg["type"] == "requirements.txt"
                    ]
                }
            }
        )
        # Build the user packages
        state.update(
            {
                "output_blocks": {
                    "build": [
                        {
                            "block": docker_run_cmd(
                                [
                                    "mkdir -p /usr/share/ou/python/user",
                                    f'echo "{user_packages}" > /usr/share/ou/python/user/requirements-0.txt',
                                ]
                            ),
                            "weight": 161,
                        },
                        {
                            "block": docker_run_cmd(
                                [
                                    f"pip wheel --no-cache-dir -w /usr/share/ou/python/user -r /usr/share/ou/python/user/requirements-0.txt {requirement_files}"  # noqa: E501
                                ]
                            ),
                            "weight": 164,
                        },
                    ],
                    "deploy": [
                        {
                            "block": docker_run_cmd(
                                [
                                    "pip install --no-index --no-deps /usr/share/ou/python/user/*.whl",
                                ]
                            ),
                            "weight": 163,
                        },
                    ],
                }
            }
        )
