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

retemplar supports multiple template processing engines that can be mixed and matched. The managed path pattern determines which files are processed by each engine, and only the destination needs to be configured:

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

### 4. Jinja2 Engine

Simple Jinja2 templating for file content and paths:

```yaml
managed_paths:
  - path: "templates/**"
    strategy: enforce
    engine: jinja
    engine_options:
      jinja_dst: . # Output to repo root
      variables:
        project_name: my-service
        version: "1.0.0"
```

Template files can use Jinja2 syntax:

```yaml
# template/config.yml.j2
service_name: { { project_name } }
version: { { version } }
debug: { { debug | default(false) } }
```

### 5. Cookiecutter Engine

Full Cookiecutter template support with hooks and project generation:

```yaml
managed_paths:
  - path: "cc/**" # Processes files from cc/ subdirectory
    strategy: enforce
    engine: cookiecutter
    engine_options:
      cookiecutter_dst: . # Output to repo root
```

The `cc/**` pattern automatically tells the engine to:

1. Process files from the `cc/` subdirectory in the template
2. Strip the `cc/` prefix from file paths
3. Apply cookiecutter processing
4. Output files to the root level (due to `cookiecutter_dst: .`)

Template structure:

```
template-repo/
├── cc/
│   ├── cookiecutter.json       # Variables configuration
│   ├── hooks/                  # Pre/post generation hooks
│   │   ├── pre_gen_project.py
│   │   └── post_gen_project.py
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

  # Jinja2 templating
  - path: "templates/**"
    strategy: enforce
    engine: jinja
    engine_options:
      jinja_dst: .
      variables:
        service_name: my-service

  # Full Cookiecutter templating
  - path: "cc/**"
    strategy: enforce
    engine: cookiecutter
    engine_options:
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

  - path: "cc/**"
    strategy: enforce
    engine: cookiecutter
    engine_options:
      cookiecutter_dst: .
```

### Custom Engine Integration

You can create custom engines by pointing to local Python files in your lockfile:

**Create a custom engine file** (`./my_engine.py`):

```python
from pydantic import BaseModel, ConfigDict

class MyEngineOptions(BaseModel):
    """Options for my custom engine."""
    template_vars: dict[str, str] = {}
    uppercase: bool = False
    model_config = ConfigDict(extra='forbid')

def process_files(src_files, engine_options):
    """Custom engine that processes files with Jinja2-like templating."""
    processed_files = {}

    for path, content in src_files.items():
        if isinstance(content, str):
            # Simple variable substitution
            processed_content = content
            for var_name, var_value in engine_options.template_vars.items():
                processed_content = processed_content.replace(
                    f"{{{{{var_name}}}}}", var_value
                )

            if engine_options.uppercase:
                processed_content = processed_content.upper()

            processed_files[path] = processed_content
        else:
            # Pass through binary files unchanged
            processed_files[path] = content

    return processed_files

# Required for options validation
options_class = MyEngineOptions
```

**Use it in your lockfile**:

```yaml
# .retemplar.lock
managed_paths:
  - path: "templates/**"
    strategy: enforce
    engine: "./my_engine.py" # Local file path
    engine_options:
      template_vars:
        project_name: "my-awesome-project"
        author: "John Doe"
      uppercase: false

  - path: "configs/**"
    strategy: enforce
    engine: "../shared-engines/yaml_processor.py" # Relative path
    engine_options:
      indent: 2
```

**Engine file requirements**:

- Must define `process_files(src_files, engine_options)` function
- Must define `options_class` (Pydantic model for validation)
- Function should return `dict[str, str | bytes]` mapping paths to content
- Engines can transform file paths by changing dictionary keys

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

  - path: "service-template/**"
    strategy: enforce
    engine: cookiecutter
    engine_options:
      cookiecutter_dst: .

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
