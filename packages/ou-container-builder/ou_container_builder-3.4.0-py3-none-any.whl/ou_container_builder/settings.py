"""Configuration settings."""

import shlex
import sys
from copy import deepcopy
from typing import Annotated, Any, Literal

from pydantic import (
    BaseModel,
    Field,
    HttpUrl,
    ValidationError,
    constr,
    create_model,
    model_validator,
)
from rich import print as cli_print
from yaml import safe_load

from ou_container_builder import packs


class Module(BaseModel):
    """Settings for the module configuration."""

    code: constr(min_length=1)
    presentation: constr(min_length=1)


class Image(BaseModel):
    """Settings for the Docker image configuration."""

    base: constr(min_length=1) = "python:3.11-bookworm"
    user: constr(min_length=1) = "ou"


class EnvironmentVariable(BaseModel):
    """Settings for additional environment variables."""

    name: constr(min_length=1)
    value: str = ""


class Arg(BaseModel):
    """Docker argument."""

    name: constr(min_length=1)
    value: str | None = None


class Server(BaseModel):
    """Settings for the core server configuration."""

    default_path: constr(min_length=1) = "/"
    access_token: str | None = None
    wrapper_host: str | None = "*.open.ac.uk"


class Content(BaseModel):
    """Settings for the content configuration."""

    source: constr(min_length=1)
    target: str = ""
    overwrite: Literal["always"] | Literal["never"]


class AptDebLine(BaseModel):
    """Settings for an APT deb line."""

    url: HttpUrl
    distribution: constr(min_length=1)
    component: constr(min_length=1)


class AptSource(BaseModel):
    """Settings for a single APT source."""

    name: constr(min_length=1)
    key_url: HttpUrl
    dearmor: bool = True
    deb: AptDebLine


class Sources(BaseModel):
    """Settings for the additional sources configuration."""

    apt: list[AptSource] = []


class AptPackageLists(BaseModel):
    """Settings for a list of apt packages for build and deploy stages."""

    core: list[constr(min_length=1)] = []
    build: list[constr(min_length=1)] = []
    deploy: list[constr(min_length=1)] = []

    @model_validator(mode="before")
    @classmethod
    def add_stages(cls: "AptPackageLists", data: Any) -> Any:
        """If only a list of packages is given, convert that to the stage structure."""
        if isinstance(data, list):
            return {"build": deepcopy(data), "deploy": deepcopy(data)}
        return data


class PipPackageEntry(BaseModel):
    """Settings for a single entry for a pip installation.

    Can either represent a single file or a requirements file.
    """

    name: constr(min_length=1)
    type: Literal["package"] | Literal["requirements.txt"] | None = "package"

    @model_validator(mode="before")
    @classmethod
    def convert_simple_packages(cls: "PipPackageLists", data: Any) -> Any:
        """If only a list of packages is given, convert that to the target structure."""
        if isinstance(data, str):
            return {"name": data, "type": "package"}
        return data


class PipPackageLists(BaseModel):
    """Settings for a list of pip packages for system and user targets."""

    system: list[PipPackageEntry] = []
    user: list[PipPackageEntry] = []

    @model_validator(mode="before")
    @classmethod
    def add_targets(cls: "PipPackageLists", data: Any) -> Any:
        """If only a list of packages is given, convert that to the target structure."""
        if isinstance(data, list):
            return {
                "system": [{"name": pkg, "type": "package"} for pkg in data],
                "user": [{"name": pkg, "type": "package"} for pkg in data],
            }
        return data


class Packages(BaseModel):
    """Settings for the packages configuration."""

    apt: AptPackageLists = AptPackageLists()
    pip: PipPackageLists = PipPackageLists()


class WebApp(BaseModel):
    """Settings for a single web application configuration."""

    path: constr(min_length=1)
    options: dict

    @model_validator(mode="before")
    @classmethod
    def convert_command_string_to_list(cls: "WebApp", data: Any) -> Any:
        """Convert command strings to lists using shlex."""
        if (
            isinstance(data, dict)
            and "options" in data
            and "command" in data["options"]
            and isinstance(data["options"]["command"], str)
        ):
            data["options"]["command"] = shlex.split(data["options"]["command"])
        return data


class BuildScript(BaseModel):
    """A script to be run during the build in the build or deploy stage."""

    stage: Literal["build"] | Literal["deploy"]
    commands: list[str]


class StartupShutdownScript(BaseModel):
    """A script to be run at startup or shutdown time."""

    stage: Literal["startup"]
    name: str
    commands: list[str]


PacksModel = create_model(
    "PacksModel",
    **{key: (value.Options | None, None) for key, value in packs.EXTENSION_PACKS.items()},
)


class OutputBlock(BaseModel):
    """Settings for a single block in the generated Dockerfile."""

    block: str
    weight: int = 999

    @model_validator(mode="before")
    @classmethod
    def convert_string_block(cls: "OutputBlock", data: Any) -> Any:
        """Convert string blocks into the dictionary structure."""
        if isinstance(data, str):
            return {"block": data}
        return data


class OutputBlocks(BaseModel):
    """Blocks for the generated Dockerfile."""

    build: list[OutputBlock] = []
    deploy: list[OutputBlock] = []


class Settings(BaseModel):
    """Application Settings."""

    version: Annotated[Literal["3"], Field(validate_default=True)] = "2"
    module: Module
    image: Image = Image()
    environment: list[EnvironmentVariable] = []
    args: list[Arg] = []
    server: Server = Server()
    content: list[Content] = []
    sources: Sources = Sources()
    packages: Packages = Packages()
    web_apps: list[WebApp] = []
    services: list[constr(min_length=1)] = []
    scripts: list[BuildScript | StartupShutdownScript] = []
    packs: PacksModel = {}
    jupyter_server_config: dict = {}
    output_blocks: OutputBlocks = OutputBlocks()


def load_settings() -> dict:
    """Load the settings from the ContainerConfig.yaml."""
    try:
        with open("ContainerConfig.yaml") as in_f:
            return Settings(**safe_load(in_f)).model_dump()
    except ValidationError as ve:
        cli_print("Unfortunately your ContainerConfig.yaml is not valid:\n")
        for err in ve.errors():
            cli_print(f"* [red]{'.'.join([str(p) for p in err['loc']])}[/red]: {err['msg']}")
        sys.exit(1)
