# Yamja

WARNING: This is pre-release software.

Yamja is an opinionated library for handling yaml configuration files and jinja2 templates - designed for configuration driven development.

It was created after I've realized that I'm repeating the same pattern in many projects. It's not big (around 100 lines of code) but it offers a consistent and ergonomic way to handle configuration files.

example usage:
```python
cfg = yamja2.load_config("./game_v1.yaml")
character = cfg.lookup('characters.marcus')
game_prompt = cfg.render('game_prompt', character=character)
```


## Features

- Load YAML configuration files
- Use Jinja2 templates within your configuration
- Support for nested configuration lookups using dot notation
- Support for environmental variables overriding lookups
- Support for jinja2 macros

## Installation

```bash
pip install yamja
```

## Usage

### Basic Configuration Loading

```python
from yamja import load_config

# Load a configuration file
config = load_config('config.yaml')

# Access values using dot notation
value = config.lookup('section.subsection.key')

# Access with default value
value = config.lookup('section.subsection.key', default='fallback')

# Access with environmental variable override
value = config.lookup('other_section.key', default=123, env_var='OTHER_KEY', cast=int)

```

### Defaults and precedence

- **Omitting `default` (or passing `...`)**: raises `KeyError` when the key is missing.
- **Precedence**: environment variable (if present) > config value > default.
- **Casting**: `cast` is applied to the selected source (env/config/default).

### Template Rendering

```yaml
# config.yaml
templates:
  greeting: "Hello {{ name }}!"
```

```python
# Render a template with variables
greeting = config.render('greeting', name='World')
```


### Including Other Config Files

```yaml
# main.yaml
include:
  - common.yaml
  - specific.yaml

additional_settings:
  key: value
```

## Requirements

- Python >= 3.12
- Jinja2 >= 3.1.4
- PyYAML >= 6.0.2

## License

MIT License - see [LICENSE](LICENSE) for details.

## Links

- [GitHub Repository](https://github.com/mobarski/yamja)

