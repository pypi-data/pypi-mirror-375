# retemplar

Keep many repos in sync with living templates — without trampling local changes. Supports multiple template engines including Cookiecutter, regex replacement, and custom processors.

## Quick Start

### 1. Adopt a Template

Make your repo adopt another repo as a template:

```bash
# Adopt a local template with default processing
retemplar adopt --template rat:local:../my-template-repo

# Adopt with specific managed paths
retemplar adopt --template rat:local:../my-template-repo \
  --managed "**/*.yml" \
  --managed "pyproject.toml" \
  --ignore "README.md"
```

This creates a `.retemplar.lock` file tracking the template relationship.

### 2. Plan Template Updates

See what changes would be applied when updating to a new template version:

```bash
# Preview upgrade to latest
retemplar plan --to rat:local:../my-template-repo

# Preview upgrade to specific version
retemplar plan --to rat:gh:org/template-repo@v1.1.0
```

### 3. Apply Changes

Apply the planned changes with variable substitution:

```bash
# Apply changes locally
retemplar apply --to rat:local:../my-template-repo

# Apply with custom variables
retemplar apply --to rat:local:../my-template-repo \
  --var project_name=my-service \
  --var version=1.0.0
```

## Template Engines

retemplar supports multiple template processing engines that can be mixed and matched:

### 1. Null Engine (Default)

Simple file copying without any processing:

```yaml
# .retemplar.lock
managed_paths:
  - path: "static/**"
    strategy: enforce
    engine: null # Default - just copy files
```

### 2. Raw String Replace Engine

Simple literal string replacement for basic templating:

```yaml
managed_paths:
  - path: "configs/**"
    strategy: enforce
    engine: raw_str_replace
    engine_options:
      variables:
        PROJECT_NAME: my-service
        VERSION: "1.0.0"
```

Template files can contain literal strings that get replaced:

```yaml
# template/config.yml
service_name: PROJECT_NAME
version: VERSION
```

### 3. Regex Replace Engine

Advanced pattern matching with regex support:

```yaml
managed_paths:
  - path: "*.md"
    strategy: enforce
    engine: regex_replace
    engine_options:
      rules:
        - pattern: "v\\d+\\.\\d+\\.\\d+"
          replacement: "v2.0.0"
          literal: false # Use regex
        - pattern: "old-name"
          replacement: "new-name"
          literal: true # Literal string
```

### 4. Cookiecutter Engine

Full Cookiecutter template support with Jinja2 templating:

```yaml
managed_paths:
  - path: "cc/**"
    strategy: enforce
    engine: cookiecutter
    engine_options:
      cookiecutter_src: cc # Subdirectory in template
      cookiecutter_dst: . # Output to repo root
```

Template structure:

```
template-repo/
├── cc/
│   ├── cookiecutter.json       # Variables configuration
│   └── {{cookiecutter.project_slug}}/
│       ├── pyproject.toml   # Jinja2 templates
│       ├── src/
│       └── tests/
└── .retemplar.lock
```

## Configuration

### Lockfile (`.retemplar.lock`)

After running `adopt`, you'll get a lockfile like:

```yaml
schema_version: 0.1.0
template_ref: rat:local:../template-repo
managed_paths:
  # Static files - no processing
  - path: ".github/workflows/**"
    strategy: enforce
    engine: null

  # Configuration with variable substitution
  - path: "configs/*.yml"
    strategy: enforce
    engine: raw_str_replace
    engine_options:
      variables:
        service_name: my-service
        version: "1.0.0"

  # Advanced pattern replacement
  - path: "docs/**/*.md"
    strategy: enforce
    engine: regex_replace
    engine_options:
      rules:
        - pattern: "template-name"
          replacement: "my-service"
          literal: true

  # Full Cookiecutter templating
  - path: "src/**"
    strategy: enforce
    engine: cookiecutter
    engine_options:
      cookiecutter_src: cookiecutter
      cookiecutter_dst: .

ignore_paths:
  - "README.md"
  - "local-configs/**"

# Global engine (optional)
engine: null # Default engine for unspecified paths
```

### Engine Processing Order

Files are processed in the order they appear in `managed_paths`. Later patterns override earlier ones for conflicting files:

```yaml
managed_paths:
  - path: "**" # Process everything with null engine
    engine: null
  - path: "*.yml" # Override: process YAML with variables
    engine: raw_str_replace
  - path: "app.yml" # Override: process app.yml with Cookiecutter
    engine: cookiecutter
```

## Advanced Usage

### Multi-Engine Templates

You can combine multiple engines in a single template:

```yaml
# Template provides both static and dynamic content
managed_paths:
  - path: "static/**"
    strategy: enforce
    engine: null

  - path: "configs/**"
    strategy: enforce
    engine: raw_str_replace
    engine_options:
      variables:
        service_name: "{{cookiecutter.project_name}}"

  - path: "src/**"
    strategy: enforce
    engine: cookiecutter
    engine_options:
      cookiecutter_src: cookiecutter
```

### Custom Engine Integration

The engine system is designed to be extensible, though custom engine support is currently limited to development/fork scenarios.

**Current approach** (requires modifying retemplar):

```python
# In your fork/development setup
def process_files(
    src_files: dict[str, str | bytes],
    engine_options: MyEngineOptions
) -> dict[str, str | bytes]:
    # Process files and return with final output paths
    return processed_files

# Add to registry.py ENGINE_REGISTRY
'my_engine': EngineRegistryEntry(my_engine.process_files, MyEngineOptions)
```

**Planned improvements** for user-friendly custom engines:

- Plugin system via Python entry points
- Configuration-based engine loading
- Directory-based engine discovery

For now, consider contributing new engines to the main project or using the existing engines with creative configurations.

### Variable Inheritance

Variables cascade from multiple sources:

1. **Lockfile global variables** (lowest priority)
2. **Engine-specific options**
3. **CLI arguments** (highest priority)

```bash
# CLI variables override lockfile
retemplar apply --to rat:local:../template \
  --var service_name=override-name \
  --var debug=true
```

## Real-World Examples

### Microservice Template

```yaml
# Template for microservices with CI/CD
managed_paths:
  - path: ".github/**"
    strategy: enforce
    engine: raw_str_replace
    engine_options:
      variables:
        service_name: USER_SERVICE

  - path: "src/**"
    strategy: enforce
    engine: cookiecutter
    engine_options:
      cookiecutter_src: service-template

  - path: "pyproject.toml"
    strategy: merge # Preserve local dependencies
```

### Documentation Template

```yaml
# Standardize docs across repos
managed_paths:
  - path: "docs/templates/**"
    strategy: enforce
    engine: regex_replace
    engine_options:
      rules:
        - pattern: "\\{\\{repo_name\\}\\}"
          replacement: "my-awesome-repo"
        - pattern: "\\{\\{team\\}\\}"
          replacement: "platform-team"
```

### Configuration Management

```yaml
# Manage config files with inheritance
managed_paths:
  - path: "configs/base/**"
    strategy: enforce
    engine: null

  - path: "configs/app.yml"
    strategy: merge
    engine: raw_str_replace
    engine_options:
      variables:
        app_name: MY_APP
        environment: production
```
