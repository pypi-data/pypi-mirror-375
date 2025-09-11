# retemplar/engines/jinja_engine.py
"""Jinja2 engine - self-contained Jinja2 template processing.

This module provides Jinja2-specific templating support for simple file templating
within existing projects. It processes files with Jinja2 syntax using retemplar variables.
"""

from pathlib import Path
from typing import Any

from jinja2 import Environment, StrictUndefined
from pydantic import BaseModel, ConfigDict, Field

from retemplar.logging import get_logger

logger = get_logger(__name__)


class JinjaEngineOptions(BaseModel):
    """Options for jinja engine.

    Processes templates with full Jinja2 templating support using retemplar variables.
    """

    # Variables for Jinja2 templating (passed by template processor)
    variables: dict[str, Any] = Field(default_factory=dict)

    # Managed path pattern (passed by template processor)
    managed_path_pattern: str = Field(
        default='',
        description='Managed path pattern to determine source prefix',
    )

    # Optional: specify subdirectory in output where to place results
    jinja_dst: Path | str = Field(
        default='',
        description='Subdirectory in output where to place results',
    )

    # Jinja2 environment settings
    autoescape: bool = Field(default=False, description='Enable autoescaping')
    keep_trailing_newline: bool = Field(
        default=True,
        description='Keep trailing newlines',
    )
    lstrip_blocks: bool = Field(
        default=False,
        description='Strip leading whitespace from blocks',
    )
    trim_blocks: bool = Field(
        default=False,
        description='Strip trailing newlines from blocks',
    )

    model_config = ConfigDict(extra='forbid')


def process_files(
    src_files: dict[str, str | bytes],
    engine_options: JinjaEngineOptions,
) -> dict[str, str | bytes]:
    """Process files using Jinja2 templating engine.

    This function processes template files using Jinja2 syntax with retemplar variables.
    Files ending in .j2 will have their content templated and the .j2 extension removed.
    File paths containing {{ }} will be templated as well.

    Args:
        src_files: Dictionary mapping relative paths to file contents
        engine_options: Engine configuration (validated as JinjaEngineOptions)

    Returns:
        Dictionary mapping output paths to processed file contents
    """
    # Create Jinja2 environment for string templating (for filenames)
    string_env = Environment(
        undefined=StrictUndefined,
        autoescape=engine_options.autoescape,
        keep_trailing_newline=engine_options.keep_trailing_newline,
        lstrip_blocks=engine_options.lstrip_blocks,
        trim_blocks=engine_options.trim_blocks,
    )

    # The managed path pattern already filtered the src_files, so use them directly
    files_to_process = src_files

    # Determine source prefix from managed path pattern
    source_prefix = _get_source_prefix_from_pattern(
        engine_options.managed_path_pattern,
    )

    processed_files = {}

    for file_path, content in files_to_process.items():
        try:
            # Remove source prefix first if it exists
            relative_path = file_path
            if source_prefix and file_path.startswith(source_prefix):
                relative_path = file_path[len(source_prefix) :].lstrip('/')

            # Template the filename if it contains Jinja2 syntax
            output_path = relative_path
            if '{{' in relative_path and '}}' in relative_path:
                template = string_env.from_string(relative_path)
                output_path = template.render(**engine_options.variables)

            # Remove .j2 extension if present
            output_path = output_path.removesuffix('.j2')

            # Apply jinja_dst prefix if specified
            if engine_options.jinja_dst:
                dst_prefix = str(engine_options.jinja_dst).rstrip('/')
                if dst_prefix and dst_prefix != '.':
                    output_path = dst_prefix + '/' + output_path

            # Process content based on type
            if isinstance(content, bytes):
                # Binary files are copied as-is
                processed_files[output_path] = content
                logger.debug(
                    'jinja_engine: copied binary file %s -> %s',
                    file_path,
                    output_path,
                )
            else:
                # Text files are templated if they contain Jinja2 syntax or end with .j2
                should_template = (
                    file_path.endswith('.j2')
                    or ('{{' in content and '}}' in content)
                    or ('{%' in content and '%}' in content)
                )

                if should_template:
                    template = string_env.from_string(content)
                    processed_content = template.render(
                        **engine_options.variables,
                    )
                    processed_files[output_path] = processed_content
                    logger.debug(
                        'jinja_engine: templated %s -> %s',
                        file_path,
                        output_path,
                    )
                else:
                    # Copy as-is if no templating needed
                    processed_files[output_path] = content
                    logger.debug(
                        'jinja_engine: copied text file %s -> %s',
                        file_path,
                        output_path,
                    )

        except Exception as e:
            logger.error(
                'jinja_engine: failed to process file %s: %s',
                file_path,
                e,
            )
            # Include original file on error to avoid data loss
            processed_files[file_path] = content

    logger.debug('jinja_engine: processed %d files', len(processed_files))
    return processed_files


def _get_source_prefix_from_pattern(pattern: str) -> str:
    """Extract the source directory prefix from a managed path pattern.

    Examples:
        'templates/**' -> 'templates/'
        'jinja/*' -> 'jinja/'
        'file.j2' -> ''
        '*' -> ''
    """
    if not pattern:
        return ''

    # Remove wildcards and extract directory part
    if pattern.endswith('/**'):
        # Pattern like 'templates/**' -> 'templates/'
        return pattern[:-3] + '/'
    if pattern.endswith('/*'):
        # Pattern like 'templates/*' -> 'templates/'
        return pattern[:-2] + '/'
    if '/' in pattern and not pattern.endswith('/'):
        # Pattern like 'templates/file.j2' -> 'templates/'
        return pattern.rsplit('/', 1)[0] + '/'
    # Pattern like '*' or 'file.j2' -> no prefix
    return ''


# Required for options validation
options_class = JinjaEngineOptions
