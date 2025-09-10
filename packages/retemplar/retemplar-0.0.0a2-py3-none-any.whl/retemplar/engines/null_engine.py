# retemplar/engines/null_engine.py
"""Null engine for copy-only functionality."""

from pydantic import BaseModel, ConfigDict

from retemplar.logging import get_logger


class NullEngineOptions(BaseModel):
    """Options for null engine (copy-only).

    This engine doesn't need any options, but we provide this model
    for consistency and potential future extension.
    """

    model_config = ConfigDict(extra='forbid')


logger = get_logger(__name__)


def process_files(
    src_files: dict[str, str | bytes],
    engine_options: NullEngineOptions,
) -> dict[str, str | bytes]:
    """Copy files without any processing.

    Args:
        src_files: Dictionary mapping relative paths to file contents
        engine_options: Validated NullEngineOptions

    Returns:
        EngineResult with 1:1 path mappings (no transformation)
    """
    _ = engine_options  # Currently no options to use

    logger.debug(
        'null_engine: copying %d files without processing',
        len(src_files),
    )

    return src_files
