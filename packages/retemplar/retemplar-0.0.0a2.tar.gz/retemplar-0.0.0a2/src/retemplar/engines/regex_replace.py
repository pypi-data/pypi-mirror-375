# retemplar/engines/regex_replace.py
"""Regex replacement engine for advanced pattern substitution."""

import re

from pydantic import BaseModel, ConfigDict, Field, model_validator

from retemplar.logging import get_logger

logger = get_logger(__name__)


class RenderRule(BaseModel):
    """Regex/literal substitution rule applied to template files during rendering.
    - When literal=True, use plain str.replace.
    - When literal=False, use re.sub with Python backrefs (\\1, \\2).
    """

    pattern: str
    replacement: str
    literal: bool = False

    model_config = ConfigDict(extra='forbid')

    @model_validator(mode='after')
    def _validate_regex_pattern(self) -> 'RenderRule':
        """Validate regex pattern when literal=False."""
        # Only validate regex patterns when not literal
        if not self.literal:
            try:
                re.compile(self.pattern)
            except re.error as e:
                raise ValueError(
                    f"Invalid regex pattern '{self.pattern}': {e}",
                ) from e
        return self


class RegexReplaceOptions(BaseModel):
    """Options for regex replacement engine.

    Applies a list of regex/literal replacement rules to text files.
    """

    rules: list[RenderRule] = Field(default_factory=list)

    model_config = ConfigDict(extra='forbid')


def process_files(
    src_files: dict[str, str | bytes],
    engine_options: RegexReplaceOptions,
) -> dict[str, str | bytes]:
    """Process files with regex/literal replacement rules.

    Args:
        src_files: Dictionary mapping relative paths to file contents
        engine_options: Validated RegexReplaceOptions

    Returns:
        Dictionary with processed file contents (no path transformation)
    """
    if not engine_options.rules:
        logger.debug(
            'regex_replace: no rules provided, copying files unchanged',
        )
        return dict(src_files)

    processed_files = {}

    for path, content in src_files.items():
        # Only process text files
        if isinstance(content, bytes):
            processed_files[path] = content
            continue

        processed_content = _apply_render_rules_text(
            content,
            engine_options.rules,
        )
        processed_files[path] = processed_content

        if processed_content != content:
            logger.debug(
                'regex_replace: processed %s with %d rules',
                path,
                len(engine_options.rules),
            )

    return processed_files


def _apply_render_rules_text(text: str, rules: list[RenderRule]) -> str:
    """Apply render rules to text content.

    Extracted from merge_utils.py apply_render_rules_text function.
    """
    result = text
    for rule in rules:
        if rule.literal:
            result = result.replace(rule.pattern, rule.replacement)
        else:
            try:
                result = re.sub(rule.pattern, rule.replacement, result)
            except re.error as e:
                raise ValueError(
                    f"Invalid regex pattern '{rule.pattern}': {e}",
                ) from e
    return result
