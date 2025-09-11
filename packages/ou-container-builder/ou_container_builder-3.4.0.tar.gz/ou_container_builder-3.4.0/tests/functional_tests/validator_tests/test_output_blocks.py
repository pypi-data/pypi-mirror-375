"""Test that the output_blocks settings work."""

from ou_container_builder.settings import OutputBlock, OutputBlocks


def test_output_block_conversion() -> None:
    settings = OutputBlocks(build=["RUN echo 'Test'"])
    assert settings.build == [OutputBlock(block="RUN echo 'Test'")]
