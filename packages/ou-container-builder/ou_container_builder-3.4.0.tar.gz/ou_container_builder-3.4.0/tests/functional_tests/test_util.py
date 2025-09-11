"""Test the utility functions."""

from ou_container_builder.util import docker_copy_cmd, docker_run_cmd


def test_basic_copy_command() -> None:
    """Test the basic copy command."""
    assert 'COPY ["source", "target"]' == docker_copy_cmd("source", "target")


def test_from_stage_copy() -> None:
    """Test that setting the from_stage parameter works."""
    assert 'COPY --from=build-stage ["source", "target"]' == docker_copy_cmd(
        "source", "target", from_stage="build-stage"
    )


def test_chmod_copy() -> None:
    """Test that chmod of the copy command works."""
    assert 'COPY --chmod=0664 ["source", "target"]' == docker_copy_cmd("source", "target", chmod="0664")


def test_from_stage_chmod_copy() -> None:
    """Test that from_stage and chmod together works."""
    assert 'COPY --from=build-stage --chmod=0664 ["source", "target"]' == docker_copy_cmd(
        "source", "target", from_stage="build-stage", chmod="0664"
    )


def test_run_single_command() -> None:
    """Test that running a single command works."""
    assert "RUN /usr/bin/sleep 60" == docker_run_cmd(["/usr/bin/sleep 60"])


def test_run_multiple_commands() -> None:
    """Test that running multiple commands works."""
    assert "RUN /usr/bin/sleep 60 && \\\n    echo $HOME" == docker_run_cmd(["/usr/bin/sleep 60", "echo $HOME"])
