# src/retemplar/template_processor.py
"""General template processing system that works with any engine."""

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pathspec

from retemplar.engines.registry import process_with_engine
from retemplar.logging import get_logger
from retemplar.utils import fs_utils
from retemplar.utils.apply_utils import apply_file_changes_from_memory
from retemplar.utils.merge_utils import best_rule
from retemplar.utils.plan_utils import (
    ChangePlanItem,
    plan_file_changes_from_memory,
)

logger = get_logger(__name__)


@dataclass
class TemplateProcessingPlan:
    """Complete template processing plan using the engine system."""

    fingerprint: str  # hash of entire template + all engine configs
    rendered_files: dict[str, str | bytes]  # ALL processed files
    engine_configs: dict[str, dict]  # engine configs used for each path pattern


def plan_template_processing(
    template_root: Path,
    dst_root: Path,
    lock_obj: Any,
    variables: dict[str, Any] = {},
) -> tuple[list[ChangePlanItem], int, TemplateProcessingPlan]:
    """Plan template processing using the new engine system.

    This provides a general template processing system
    that can use any engine based on managed_paths configuration.
    """
    # Merge variables: lockfile < CLI
    lock_variables = getattr(lock_obj, 'variables', {}) or {}
    all_variables = {**lock_variables, **variables}

    # Get all template files
    all_template_files = _get_all_template_files_as_content(template_root)

    # Group files by engine based on managed paths
    engine_groups = _group_files_by_engine(
        list(all_template_files.keys()),
        lock_obj.managed_paths or [],
        lock_obj,
    )

    # Process each group with its engine
    all_rendered_files = {}
    engine_configs = {}

    for engine_name, file_paths in engine_groups.items():
        if not file_paths:
            continue

        # Get files for this engine
        engine_files = {path: all_template_files[path] for path in file_paths}

        # Get engine options for this group
        engine_options = _get_engine_options_for_group(
            engine_name,
            file_paths,
            lock_obj,
            all_variables,
            template_root,
            dst_root,
        )
        engine_configs[engine_name] = engine_options

        # Process files with engine
        engine_rendered_files = process_with_engine(
            engine_name,
            engine_files,
            engine_options,
        )

        # Simple last-wins conflict resolution
        # Later engines in the processing order override earlier ones
        for output_path, content in engine_rendered_files.items():
            if output_path in all_rendered_files:
                logger.debug(
                    'template_processor: file conflict %s - later engine %s overrides',
                    output_path,
                    engine_name,
                )
            all_rendered_files[output_path] = content

    # Calculate fingerprint
    fingerprint = _compute_template_fingerprint(template_root, engine_configs)

    # Create plan
    template_plan = TemplateProcessingPlan(
        fingerprint=fingerprint,
        rendered_files=all_rendered_files,
        engine_configs=engine_configs,
    )

    # Get managed files (simplified - all rendered files are managed)
    managed_files = _get_managed_files_from_rendered_files(
        lock_obj,
        all_rendered_files,
    )

    change_plan_items, conflicts = plan_file_changes_from_memory(
        managed_files,
        all_rendered_files,
        lock_obj,
        dst_root,
    )

    return change_plan_items, conflicts, template_plan


def apply_template_processing_plan(
    plan_items: list[ChangePlanItem],
    template_plan: TemplateProcessingPlan,
    dst_root: Path,
    lock_obj: Any,
) -> tuple[int, int]:
    """Apply a pre-computed template processing plan."""
    # Apply changes using the rendered files
    files_changed, conflicts_resolved = apply_file_changes_from_memory(
        plan_items,
        template_plan.rendered_files,
        dst_root,
        lock_obj,
    )

    return files_changed, conflicts_resolved


def _get_all_template_files_as_content(
    template_root: Path,
) -> dict[str, str | bytes]:
    """Get all template files with their content."""
    files = {}

    for file_path in fs_utils.list_files(template_root):
        full_path = template_root / file_path
        try:
            # Try to read as text first
            content = full_path.read_text(encoding='utf-8')
            files[file_path] = content
        except UnicodeDecodeError:
            # Fall back to binary
            content = full_path.read_bytes()
            files[file_path] = content

    return files


def _group_files_by_engine(
    file_paths: list[str],
    managed_paths: list,
    lock_obj: Any,
) -> dict[str, list[str]]:
    """Group files by engine based on managed_paths configuration."""
    engine_groups = {}

    # Default engine from lockfile
    default_engine = getattr(lock_obj, 'engine', None) or 'null'

    logger.debug('template_processor: using default engine %s', default_engine)

    for file_path in file_paths:
        # Find the best matching managed path rule
        rule = best_rule(file_path, managed_paths)

        if rule and rule.engine:
            engine_name = rule.engine
        else:
            engine_name = default_engine

        if engine_name not in engine_groups:
            engine_groups[engine_name] = []
        engine_groups[engine_name].append(file_path)

    return engine_groups


def _get_engine_options_for_group(
    engine_name: str,
    file_paths: list[str],
    lock_obj: Any,
    variables: dict[str, Any],
    template_root: Path | None = None,
    dst_root: Path | None = None,
) -> dict[str, Any]:
    """Get engine options for a group of files."""
    # Start with default options from lockfile
    base_options = getattr(lock_obj, 'engine_options', {}) or {}

    # Find the first managed path that matches and has engine options
    for file_path in file_paths:
        rule = best_rule(file_path, lock_obj.managed_paths or [])
        if rule and rule.engine == engine_name and rule.engine_options:
            # Merge rule-specific options
            base_options = {**base_options, **rule.engine_options}
            break

    # Add engine-specific options
    if engine_name == 'raw_str_replace':
        return {'variables': variables, **base_options}
    if engine_name == 'regex_replace':
        return base_options  # Rules should be in engine_options already
    if engine_name == 'cookiecutter':
        # Cookiecutter uses its own cookiecutter.json, not retemplar variables
        return {
            'template_root': str(template_root) if template_root else '',
            'dst_root': str(dst_root) if dst_root else '',
            'lock_obj': lock_obj,
            **base_options,
        }
    # null or custom engines
    return base_options


def _compute_template_fingerprint(
    template_root: Path,
    engine_configs: dict[str, dict],
) -> str:
    """Compute fingerprint of template + all engine configurations."""
    h = hashlib.sha256()

    # Hash engine configurations (exclude non-serializable objects)
    serializable_configs = {}
    for engine_name, config in engine_configs.items():
        # Create a clean config dict without complex objects
        clean_config = {}
        for key, value in config.items():
            if key in ('lock_obj',):
                # Skip non-serializable objects
                continue
            if isinstance(value, (str, int, float, bool, list, dict)):
                clean_config[key] = value
            else:
                # Convert other types to string representation
                clean_config[key] = str(value)
        serializable_configs[engine_name] = clean_config

    h.update(json.dumps(serializable_configs, sort_keys=True).encode())

    # Hash all template files
    for file_path in sorted(fs_utils.list_files(template_root)):
        # Skip hooks directory for consistency
        if file_path.startswith('hooks/'):
            continue

        h.update(file_path.encode())
        full_path = template_root / file_path
        try:
            h.update(full_path.read_bytes())
        except Exception:
            h.update(b'<unreadable>')

    return h.hexdigest()


def _get_managed_files_from_rendered_files(
    lock_obj: Any,
    all_rendered_files: dict[str, str | bytes],
) -> dict[str, object]:
    """Get managed files from rendered files.

    For simplicity, all rendered files are considered managed.
    """
    managed_files = {}

    # Use pathspec for gitignore-style ignore patterns
    ignore_spec = pathspec.PathSpec.from_lines(
        'gitwildmatch',
        lock_obj.ignore_paths or [],
    )

    # All non-ignored files are managed
    for output_file_path in all_rendered_files:
        # Check if file should be ignored
        if ignore_spec.match_file(output_file_path):
            continue

        # Use a simple default rule for all managed files
        managed_files[output_file_path] = type(
            'Rule',
            (),
            {'path': '**', 'strategy': 'enforce'},
        )()

    return managed_files
