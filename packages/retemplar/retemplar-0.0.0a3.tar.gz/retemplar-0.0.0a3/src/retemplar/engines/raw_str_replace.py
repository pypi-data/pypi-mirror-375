# retemplar/engines/raw_str_replace.py
"""Raw string replacement engine for simple variable substitution."""

from pydantic import BaseModel, ConfigDict, Field

from retemplar.logging import get_logger


class RawStrReplaceOptions(BaseModel):
    """Options for raw string replacement engine.

    Performs simple literal string substitution in text files.
    """

    variables: dict[str, str] = Field(default_factory=dict)

    model_config = ConfigDict(extra='forbid')


logger = get_logger(__name__)


def process_files(
    src_files: dict[str, str | bytes],
    engine_options: RawStrReplaceOptions,
) -> dict[str, str | bytes]:
    """Process files with raw string replacement.

    Args:
        src_files: Dictionary mapping relative paths to file contents
        engine_options: Validated RawStrReplaceOptions

    Returns:
        Dictionary with processed file contents (no path transformation)
    """
    if not engine_options.variables:
        logger.debug(
            'raw_str_replace: no variables provided, copying files unchanged',
        )
        return dict(src_files)

    processed_files = {}

    for path, content in src_files.items():
        # Only process text files
        if isinstance(content, bytes):
            processed_files[path] = content
            continue

        processed_content = content

        # Simple literal string replacement for each variable
        for var_name, var_value in engine_options.variables.items():
            # Replace literal string occurrences
            processed_content = processed_content.replace(
                var_name,
                str(var_value),
            )

        processed_files[path] = processed_content

        if processed_content != content:
            logger.debug(
                'raw_str_replace: processed %s with %d variables',
                path,
                len(engine_options.variables),
            )

    return processed_files
