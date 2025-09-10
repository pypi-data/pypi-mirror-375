# tests/test_engines.py
"""Tests for engine adapters."""

import pytest

from retemplar.engines.null_engine import process_files as null_process
from retemplar.engines.raw_str_replace import (
    process_files as str_replace_process,
)
from retemplar.engines.registry import get_engine, list_engines


def test_null_engine():
    """Test null engine copies files without modification."""
    from retemplar.engines.null_engine import NullEngineOptions

    files = {
        'README.md': 'Hello {{name}}!',
        'binary.dat': b'\x00\x01\x02\x03',
    }

    options = NullEngineOptions()
    result = null_process(files, options)

    assert result == files
    assert result['README.md'] == 'Hello {{name}}!'
    assert result['binary.dat'] == b'\x00\x01\x02\x03'


def test_str_replace_engine():
    """Test raw string replacement engine."""
    from retemplar.engines.raw_str_replace import RawStrReplaceOptions

    files = {
        'README.md': 'Hello NAME! Project: PROJECT',
        'config.yml': 'owner: OWNER\nrepo: REPO',
        'binary.dat': b'\x00\x01\x02\x03',
    }

    options = RawStrReplaceOptions(
        variables={
            'NAME': 'World',
            'PROJECT': 'retemplar',
            'OWNER': 'acme',
            'REPO': 'main-svc',
        },
    )

    result = str_replace_process(files, options)

    assert result['README.md'] == 'Hello World! Project: retemplar'
    assert result['config.yml'] == 'owner: acme\nrepo: main-svc'
    assert result['binary.dat'] == b'\x00\x01\x02\x03'  # Binary unchanged


def test_str_replace_engine_no_variables():
    """Test str replace engine with no variables."""
    from retemplar.engines.raw_str_replace import RawStrReplaceOptions

    files: dict[str, str | bytes] = {'test.txt': 'Hello {{name}}!'}
    options = RawStrReplaceOptions()

    result = str_replace_process(files, options)

    assert result == files


def test_engine_registry():
    """Test engine registry functionality."""
    # Test listing engines
    engines = list_engines()
    assert 'null' in engines
    assert 'raw_str_replace' in engines
    assert 'regex_replace' in engines

    # Test getting engines
    null_engine = get_engine('null')
    assert callable(null_engine)

    str_replace_engine = get_engine('raw_str_replace')
    assert callable(str_replace_engine)

    # Test default engine
    default_engine = get_engine(None)
    assert default_engine == null_engine

    # Test invalid engine
    with pytest.raises(ValueError, match='Unknown engine'):
        get_engine('invalid_engine')


def test_engine_option_validation():
    """Test that all engines work with typed options."""
    from retemplar.engines.null_engine import NullEngineOptions
    from retemplar.engines.null_engine import process_files as null_process
    from retemplar.engines.raw_str_replace import RawStrReplaceOptions
    from retemplar.engines.raw_str_replace import process_files as str_process

    files: dict[str, str | bytes] = {'test.txt': 'content'}

    # Null engine with typed options
    options = NullEngineOptions()
    result = null_process(files, options)
    assert result == files

    # Raw str replace with typed options
    str_options = RawStrReplaceOptions(variables={'name': 'test'})
    result = str_process(files, str_options)
    assert result == files  # No substitution since no {{}} in content

    # Test Pydantic validation on creation
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        RawStrReplaceOptions(variables='invalid')  # type: ignore # Should be dict


def test_registry_validation_helpers():
    """Test registry validation helper functions."""
    from pydantic import ValidationError

    from retemplar.engines.null_engine import NullEngineOptions
    from retemplar.engines.raw_str_replace import RawStrReplaceOptions
    from retemplar.engines.regex_replace import RegexReplaceOptions
    from retemplar.engines.registry import (
        get_engine_options_schema,
        validate_engine_options,
    )

    # Test schema retrieval
    assert get_engine_options_schema('null') == NullEngineOptions
    assert get_engine_options_schema('raw_str_replace') == RawStrReplaceOptions
    assert get_engine_options_schema('regex_replace') == RegexReplaceOptions

    with pytest.raises(ValueError, match='Unknown engine'):
        get_engine_options_schema('invalid')

    # Test option validation
    null_options = validate_engine_options('null', {})
    assert isinstance(null_options, NullEngineOptions)

    str_options = validate_engine_options(
        'raw_str_replace',
        {'variables': {'name': 'test'}},
    )
    assert isinstance(str_options, RawStrReplaceOptions)
    assert str_options.variables == {'name': 'test'}

    # Invalid options should raise ValidationError
    with pytest.raises(ValidationError):
        validate_engine_options('null', {'invalid_field': 'value'})

    with pytest.raises(ValueError, match='Unknown engine'):
        validate_engine_options('invalid', {})


def test_process_with_engine():
    """Test centralized process_with_engine function."""
    from pydantic import ValidationError

    from retemplar.engines.registry import process_with_engine

    files: dict[str, str | bytes] = {
        'test.txt': 'Hello name!',
        'binary.dat': b'\x00\x01\x02',
    }

    # Test null engine
    result = process_with_engine('null', files, {})
    assert result == files

    # Test raw string replace
    result = process_with_engine(
        'raw_str_replace',
        files,
        {'variables': {'name': 'World'}},
    )
    assert result['test.txt'] == 'Hello World!'
    assert result['binary.dat'] == b'\x00\x01\x02'

    # Test validation error
    with pytest.raises(ValidationError):
        process_with_engine('null', files, {'invalid_field': 'value'})

    # Test unknown engine
    with pytest.raises(ValueError, match='Unknown engine'):
        process_with_engine('invalid', files, {})


def test_regex_replace_engine():
    """Test regex replacement engine."""
    from retemplar.engines.registry import process_with_engine

    files: dict[str, str | bytes] = {
        'version.txt': 'Version: v1.0.0\nBuild: dev',
        'config.json': '{"version": "v1.0.0", "env": "development"}',
        'binary.dat': b'\x00\x01\x02\x03',
    }

    # Test literal replacement
    result = process_with_engine(
        'regex_replace',
        files,
        {
            'rules': [
                {'pattern': 'v1.0.0', 'replacement': 'v2.0.0', 'literal': True},
            ],
        },
    )

    assert result['version.txt'] == 'Version: v2.0.0\nBuild: dev'
    assert (
        result['config.json'] == '{"version": "v2.0.0", "env": "development"}'
    )
    assert result['binary.dat'] == b'\x00\x01\x02\x03'  # Binary unchanged

    # Test regex replacement with backreferences
    regex_result = process_with_engine(
        'regex_replace',
        files,
        {
            'rules': [
                {
                    'pattern': r'Version: (v\d+\.\d+\.\d+)',
                    'replacement': r'Release: \1-stable',
                    'literal': False,
                },
            ],
        },
    )

    assert regex_result['version.txt'] == 'Release: v1.0.0-stable\nBuild: dev'

    # Test multiple rules
    multi_result = process_with_engine(
        'regex_replace',
        files,
        {
            'rules': [
                {'pattern': 'v1.0.0', 'replacement': 'v2.0.0', 'literal': True},
                {
                    'pattern': 'dev',
                    'replacement': 'production',
                    'literal': True,
                },
            ],
        },
    )

    assert multi_result['version.txt'] == 'Version: v2.0.0\nBuild: production'


def test_regex_replace_validation():
    """Test regex replacement engine validation."""
    from pydantic import ValidationError

    from retemplar.engines.regex_replace import RegexReplaceOptions, RenderRule
    from retemplar.engines.registry import process_with_engine

    # Test invalid regex pattern
    with pytest.raises(ValidationError, match='Invalid regex pattern'):
        RenderRule(pattern='[invalid', replacement='test', literal=False)

    # Test valid literal pattern (no regex validation)
    rule = RenderRule(pattern='[invalid', replacement='test', literal=True)
    assert rule.pattern == '[invalid'

    # Test empty rules (should work)
    options = RegexReplaceOptions()
    assert options.rules == []

    files: dict[str, str | bytes] = {'test.txt': 'content'}
    result = process_with_engine('regex_replace', files, {'rules': []})
    assert result == files
