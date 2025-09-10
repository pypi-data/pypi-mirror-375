# retemplar/engines/registry.py
"""Engine registry for managing different template processing engines."""

from collections.abc import Callable
from typing import Any

from retemplar.engines import (
    cookiecutter_engine,
    null_engine,
    raw_str_replace,
    regex_replace,
)
from retemplar.engines.cookiecutter_engine import CookiecutterEngineOptions
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
    'cookiecutter': EngineRegistryEntry(
        cookiecutter_engine.process_files,
        CookiecutterEngineOptions,
    ),
}


def get_engine(engine_name: str | None) -> EngineProcessor:
    """Get engine processor by name.

    Args:
        engine_name: Name of engine, or None for default (null)

    Returns:
        Engine processor function

    Raises:
        ValueError: If engine name is not registered
    """
    if engine_name is None:
        engine_name = 'null'

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
        engine_name: Name of the engine

    Returns:
        Pydantic model class for the engine's options

    Raises:
        ValueError: If engine name is unknown
    """
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
