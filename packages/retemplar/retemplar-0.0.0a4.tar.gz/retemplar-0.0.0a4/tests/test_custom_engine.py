# tests/test_custom_engine.py
"""Tests for custom engine loading from files."""

import tempfile
from pathlib import Path

import pytest
from pydantic import BaseModel

from retemplar.engines.registry import (
    get_engine,
    get_engine_options_schema,
    process_with_engine,
)


def test_load_engine_from_file():
    """Test loading a custom engine from a Python file."""
    # Create a temporary engine file
    engine_code = '''
from pydantic import BaseModel, ConfigDict

class CustomEngineOptions(BaseModel):
    """Options for the custom engine."""
    prefix: str = "custom_"
    model_config = ConfigDict(extra='forbid')

def process_files(src_files, engine_options):
    """Custom engine that adds a prefix to all file paths."""
    processed_files = {}
    for path, content in src_files.items():
        new_path = engine_options.prefix + path
        if isinstance(content, str):
            processed_files[new_path] = f"PROCESSED: {content}"
        else:
            processed_files[new_path] = content
    return processed_files

# Required for options validation
options_class = CustomEngineOptions
'''

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(engine_code)
        engine_file = f.name

    try:
        # Test loading the engine
        engine_processor = get_engine(engine_file)
        assert callable(engine_processor)

        # Test loading options schema
        options_schema = get_engine_options_schema(engine_file)
        assert issubclass(options_schema, BaseModel)

        # Test processing files
        src_files = {
            'test.txt': 'Hello world',
            'data.bin': b'\\x00\\x01\\x02',
        }

        result = process_with_engine(
            engine_file,
            src_files,
            {'prefix': 'custom_'},
        )

        expected = {
            'custom_test.txt': 'PROCESSED: Hello world',
            'custom_data.bin': b'\\x00\\x01\\x02',
        }

        assert result == expected

    finally:
        # Clean up
        Path(engine_file).unlink()


def test_load_engine_file_not_found():
    """Test error handling for missing engine files."""
    with pytest.raises(ValueError, match='Engine file not found'):
        get_engine('/nonexistent/engine.py')


def test_load_engine_not_python_file():
    """Test error handling for non-Python files."""
    with tempfile.NamedTemporaryFile(
        mode='w',
        suffix='.txt',
        delete=False,
    ) as f:
        f.write('not python code')
        invalid_file = f.name

    try:
        with pytest.raises(ValueError, match='Engine file must be a .py file'):
            get_engine(invalid_file)
    finally:
        Path(invalid_file).unlink()


def test_load_engine_missing_process_files():
    """Test error handling for engine files without process_files function."""
    engine_code = """
# Missing process_files function
def other_function():
    pass
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(engine_code)
        engine_file = f.name

    try:
        with pytest.raises(
            ValueError,
            match="must define a 'process_files' function",
        ):
            get_engine(engine_file)
    finally:
        Path(engine_file).unlink()


def test_load_engine_missing_options_class():
    """Test error handling for engine files without options_class."""
    engine_code = """
def process_files(src_files, engine_options):
    return src_files

# Missing options_class
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(engine_code)
        engine_file = f.name

    try:
        with pytest.raises(ValueError, match="must define 'options_class'"):
            get_engine_options_schema(engine_file)
    finally:
        Path(engine_file).unlink()


def test_relative_path_detection():
    """Test that relative paths are detected as file paths."""
    # These should be treated as file paths, not built-in engines
    file_paths = [
        './my_engine.py',
        '../shared/engine.py',
        'engines/custom.py',
        '/absolute/path/engine.py',
        'C:\\\\Windows\\\\engine.py',  # Windows absolute path
    ]

    for path in file_paths:
        # Should try to load as file (will fail since files don't exist)
        with pytest.raises(ValueError, match='Engine file not found'):
            get_engine(path)


def test_builtin_engines_still_work():
    """Test that built-in engines still work after adding file loading."""
    # Test that null engine still works
    null_engine = get_engine('null')
    assert callable(null_engine)

    # Test that we can process with built-in engines
    src_files: dict[str, str | bytes] = {'test.txt': 'content'}
    result = process_with_engine('null', src_files, {})
    assert result == src_files
