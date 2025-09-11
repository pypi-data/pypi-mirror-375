# retemplar/engines/cookiecutter_engine.py
"""Real cookiecutter engine using the cookiecutter library.

This engine uses the actual cookiecutter library to generate projects from
cookiecutter templates, providing full cookiecutter compatibility including
hooks, context generation, and proper project structure handling.
"""

import tempfile
from pathlib import Path
from typing import Any

from cookiecutter.main import cookiecutter
from pydantic import BaseModel, ConfigDict, Field

from retemplar.logging import get_logger
from retemplar.utils import fs_utils

logger = get_logger(__name__)


class CookiecutterEngineOptions(BaseModel):
    """Options for real cookiecutter engine."""

    # Optional: specify subdirectory in output where to place results
    cookiecutter_dst: Path | str = Field(
        default='',
        description='Subdirectory in output where to place results',
    )

    # Managed path pattern (passed by template processor)
    managed_path_pattern: str = Field(
        default='',
        description='Managed path pattern to determine source prefix',
    )

    # Any extra context to pass to cookiecutter (overrides cookiecutter.json)
    extra_context: dict[str, Any] = Field(default_factory=dict)

    # Whether to accept default values without prompting (always True for retemplar)
    no_input: bool = Field(default=True)

    # Whether to overwrite existing files
    overwrite_if_exists: bool = Field(default=True)

    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)


def process_files(
    src_files: dict[str, str | bytes],
    engine_options: CookiecutterEngineOptions,
) -> dict[str, str | bytes]:
    """Process files using real cookiecutter engine.

    This engine works with the retemplar pattern - it takes src_files as input,
    writes them to a temporary cookiecutter template, runs cookiecutter on it,
    and returns the generated files.

    Args:
        src_files: Dictionary mapping relative paths to file contents
        engine_options: Engine configuration

    Returns:
        Dictionary mapping paths to processed file contents
    """
    # Check if cookiecutter is available
    if cookiecutter is None:
        raise RuntimeError(
            'cookiecutter library not installed. '
            'Install with: pip install cookiecutter',
        )

    # The managed path pattern already filtered the src_files, so use them directly
    files_to_process = src_files

    if not files_to_process:
        logger.warning('cookiecutter_engine: no files found to process')
        return {}

    # Create temporary cookiecutter template directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_template_dir = Path(temp_dir) / 'template'
        temp_output_dir = Path(temp_dir) / 'output'
        temp_template_dir.mkdir()

        # Write all src_files to temporary template directory
        # Determine source prefix from managed path pattern
        source_prefix = _get_source_prefix_from_pattern(
            engine_options.managed_path_pattern,
        )

        for file_path, content in files_to_process.items():
            # Remove source prefix to get relative path within cookiecutter template
            if source_prefix and file_path.startswith(source_prefix):
                relative_path = file_path[len(source_prefix) :].lstrip('/')
            else:
                relative_path = file_path

            full_path = temp_template_dir / relative_path
            full_path.parent.mkdir(parents=True, exist_ok=True)

            if isinstance(content, bytes):
                full_path.write_bytes(content)
            else:
                full_path.write_text(content, encoding='utf-8')

        # Validate cookiecutter.json exists
        cookiecutter_json = temp_template_dir / 'cookiecutter.json'
        if not cookiecutter_json.exists():
            raise ValueError(
                'Not a valid cookiecutter template - missing cookiecutter.json',
            )

        try:
            # Generate project using cookiecutter
            result_path = cookiecutter(
                template=str(temp_template_dir),
                output_dir=str(temp_output_dir),
                extra_context=engine_options.extra_context,
                no_input=engine_options.no_input,
                overwrite_if_exists=engine_options.overwrite_if_exists,
            )

            result_path = Path(result_path)

            # Read all generated files
            generated_files = {}

            if result_path.exists():
                for file_path in fs_utils.list_files(result_path):
                    full_path = result_path / file_path

                    # Apply cookiecutter_dst prefix if specified
                    output_path = file_path
                    if engine_options.cookiecutter_dst:
                        dst_prefix = str(
                            engine_options.cookiecutter_dst,
                        ).rstrip('/')
                        if dst_prefix and dst_prefix != '.':
                            output_path = dst_prefix + '/' + file_path

                    try:
                        # Try to read as text first
                        content = full_path.read_text(encoding='utf-8')
                        generated_files[output_path] = content
                    except UnicodeDecodeError:
                        # Fall back to binary
                        content = full_path.read_bytes()
                        generated_files[output_path] = content

            logger.debug(
                'cookiecutter_engine: generated %d files from %d source files',
                len(generated_files),
                len(files_to_process),
            )

            return generated_files

        except Exception as e:
            logger.error(
                'cookiecutter_engine: failed to generate project: %s',
                e,
            )
            raise


def _get_source_prefix_from_pattern(pattern: str) -> str:
    """Extract the source directory prefix from a managed path pattern.

    Examples:
        'cc/**' -> 'cc/'
        'templates/cookiecutter/**' -> 'templates/cookiecutter/'
        'cookiecutter.json' -> ''
        '*' -> ''
    """
    if not pattern:
        return ''

    # Remove wildcards and extract directory part
    if pattern.endswith('/**'):
        # Pattern like 'cc/**' -> 'cc/'
        return pattern[:-3] + '/'
    if pattern.endswith('/*'):
        # Pattern like 'cc/*' -> 'cc/'
        return pattern[:-2] + '/'
    if '/' in pattern and not pattern.endswith('/'):
        # Pattern like 'cc/cookiecutter.json' -> 'cc/'
        return pattern.rsplit('/', 1)[0] + '/'
    # Pattern like '*' or 'cookiecutter.json' -> no prefix
    return ''


# Required for options validation
options_class = CookiecutterEngineOptions
