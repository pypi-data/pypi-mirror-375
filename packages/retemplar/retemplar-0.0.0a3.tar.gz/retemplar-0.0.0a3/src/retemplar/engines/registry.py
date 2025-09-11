# retemplar/engines/registry.py
"""Engine registry for managing different template processing engines."""

import importlib.util
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

from retemplar.engines import (
    cookiecutter_engine,
    jinja_engine,
    null_engine,
    raw_str_replace,
    regex_replace,
)
from retemplar.engines.cookiecutter_engine import CookiecutterEngineOptions
from retemplar.engines.jinja_engine import JinjaEngineOptions
from retemplar.engines.null_engine import NullEngineOptions
from retemplar.engines.raw_str_replace import RawStrReplaceOptions
from retemplar.engines.regex_replace import RegexReplaceOptions
from retemplar.logging import get_logger

logger = get_logger(__name__)

EngineProcessor = Callable[
    [dict[str, str | bytes], Any],
    dict[str, str | bytes],
]


# Engine registry entry containing both processor and options class
class EngineRegistryEntry:
    def __init__(self, processor: EngineProcessor, options_class: type):
        self.processor = processor
        self.options_class = options_class


# Registry of available engines
ENGINE_REGISTRY: dict[str, EngineRegistryEntry] = {
    'null': EngineRegistryEntry(null_engine.process_files, NullEngineOptions),
    'raw_str_replace': EngineRegistryEntry(
        raw_str_replace.process_files,
        RawStrReplaceOptions,
    ),
    'regex_replace': EngineRegistryEntry(
        regex_replace.process_files,
        RegexReplaceOptions,
    ),
    'jinja': EngineRegistryEntry(
        jinja_engine.process_files,
        JinjaEngineOptions,
    ),
    'cookiecutter': EngineRegistryEntry(
        cookiecutter_engine.process_files,
        CookiecutterEngineOptions,
    ),
}


def get_engine(engine_name: str | None) -> EngineProcessor:
    """Get engine processor by name or file path.

    Args:
        engine_name: Name of built-in engine, file path, or None for default (null)

    Returns:
        Engine processor function

    Raises:
        ValueError: If engine name is not registered or file not found
    """
    if engine_name is None:
        engine_name = 'null'

    # Check if it's a file path (contains / or \ or ends with .py)
    if '/' in engine_name or '\\' in engine_name or engine_name.endswith('.py'):
        return _load_engine_from_file(engine_name)

    # Check built-in engines
    if engine_name not in ENGINE_REGISTRY:
        available = ', '.join(ENGINE_REGISTRY.keys())
        raise ValueError(
            f"Unknown engine '{engine_name}'. Available engines: {available}",
        )

    return ENGINE_REGISTRY[engine_name].processor


def register_engine(
    name: str,
    processor: EngineProcessor,
    options_class: type,
) -> None:
    """Register a new engine processor with its options class.

    Args:
        name: Engine name
        processor: Engine processor function
        options_class: Pydantic model class for engine options
    """
    ENGINE_REGISTRY[name] = EngineRegistryEntry(processor, options_class)
    logger.debug(f'Registered engine: {name}')


def list_engines() -> list[str]:
    """List all registered engine names."""
    return list(ENGINE_REGISTRY.keys())


def get_engine_options_schema(engine_name: str) -> type:
    """Get the Pydantic model class for an engine's options.

    Args:
        engine_name: Name of the engine or file path

    Returns:
        Pydantic model class for the engine's options

    Raises:
        ValueError: If engine name is unknown or file doesn't have options_class
    """
    # Check if it's a file path
    if '/' in engine_name or '\\' in engine_name or engine_name.endswith('.py'):
        module = _load_module_from_file(engine_name)
        if not hasattr(module, 'options_class'):
            raise ValueError(
                f"Engine file '{engine_name}' must define 'options_class'",
            )
        return module.options_class

    # Built-in engine
    if engine_name not in ENGINE_REGISTRY:
        available = ', '.join(ENGINE_REGISTRY.keys())
        raise ValueError(
            f"Unknown engine '{engine_name}'. Available engines: {available}",
        )

    return ENGINE_REGISTRY[engine_name].options_class


def validate_engine_options(
    engine_name: str,
    engine_options: dict[str, Any],
) -> Any:
    """Validate engine options against the appropriate Pydantic model.

    Args:
        engine_name: Name of the engine
        engine_options: Raw options dictionary

    Returns:
        Validated options object (specific to engine type)

    Raises:
        ValueError: If engine name is unknown
        ValidationError: If options are invalid
    """
    options_class = get_engine_options_schema(engine_name)
    return options_class.model_validate(engine_options)


def process_with_engine(
    engine_name: str,
    src_files: dict[str, str | bytes],
    engine_options: dict[str, Any],
) -> dict[str, str | bytes]:
    """Process files with specified engine, handling validation centrally.

    Args:
        engine_name: Name of engine to use
        src_files: Dictionary mapping relative paths to file contents
        engine_options: Raw engine options (will be validated)

    Returns:
        Dictionary mapping output paths to processed file contents

    Raises:
        ValueError: If engine name is unknown
        ValidationError: If options are invalid
    """
    # Get engine processor
    processor = get_engine(engine_name)

    # Validate options and convert to typed options object
    validated_options = validate_engine_options(engine_name, engine_options)

    # Process files with typed options
    return processor(src_files, validated_options)


def _load_module_from_file(file_path: str):
    """Load a Python module from a file path."""
    path = Path(file_path)
    if not path.exists():
        raise ValueError(f'Engine file not found: {file_path}')

    if not path.suffix == '.py':
        raise ValueError(f'Engine file must be a .py file: {file_path}')

    # Create module spec
    module_name = f'retemplar_engine_{path.stem}_{id(path)}'
    spec = importlib.util.spec_from_file_location(module_name, path)

    if spec is None or spec.loader is None:
        raise ValueError(f'Could not load engine from file: {file_path}')

    # Load the module
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    return module


def _load_engine_from_file(file_path: str) -> EngineProcessor:
    """Load an engine processor function from a file path."""
    module = _load_module_from_file(file_path)

    if not hasattr(module, 'process_files'):
        raise ValueError(
            f"Engine file '{file_path}' must define a 'process_files' function",
        )

    processor = module.process_files

    # Validate the function signature (basic check)
    if not callable(processor):
        raise ValueError(
            f"'process_files' in '{file_path}' must be a callable function",
        )

    logger.debug(f'Loaded engine from file: {file_path}')
    return processor  # type: ignore # Runtime validation ensures correct signature
