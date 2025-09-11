"""Utility functions for working with Docker."""


def docker_run_cmd(commands: list[str]) -> str:
    """Generate a docker run command."""
    command_string = " && \\\n    ".join(commands)
    return f"RUN {command_string}"


def docker_copy_cmd(src: str, target: str, from_stage: str | None = None, chmod: str | None = None) -> str:
    """Generate a docker copy command."""
    parts = ["COPY"]
    if from_stage is not None:
        parts.append(f"--from={from_stage}")
    if chmod is not None:
        parts.append(f"--chmod={chmod}")
    parts.append(f'["{src}", "{target}"]')
    return " ".join(parts)
