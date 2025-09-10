# Yamja

A lightweight, opinionated library for seamless YAML configuration and Jinja2 template management in Python. Yamja simplifies configuration-driven development by providing an intuitive interface for handling nested configurations, template rendering, and file merging.

## Key Features

- **Smart Configuration Loading**: Load and merge multiple YAML files with automatic conflict resolution
- **Nested Lookups**: Access deeply nested values using simple dot notation
- **Template Integration**: Seamlessly use Jinja2 templates within your YAML configurations
- **Macro Support**: Leverage Jinja2 macros for reusable template logic
- **Hierarchical Includes**: Include and merge multiple configuration files with intelligent override behavior
- **Minimal Dependencies**: Only requires Jinja2 and PyYAML

## Installation

```bash
pip install yamja
```

## Quick Start

```python
from yamja import load_config

# Load game configuration
cfg = load_config("game_config.yaml")

# Get character data using dot notation
character = cfg.lookup("characters.jane")

# Generate character prompt using template
prompt = cfg.render("character_prompt", character=character)
```

## Configuration Features

### Basic Configuration Structure

```yaml
# game_config.yaml
characters:
  jane:
    name: Jane Doe
    age: 30
    skills:
      - hacking
      - parkour
      - martial arts

templates:
  character_prompt: |
    <CHARACTER>
      <NAME>{{ character.name }}</NAME>
      <AGE>{{ character.age }}</AGE>
      <SKILLS>
        {% for skill in character.skills %}
          <SKILL>{{ skill }}</SKILL>
        {% endfor %}
      </SKILLS>
    </CHARACTER>
```

### Including Other Configurations

Yamja supports including and merging multiple configuration files:

```yaml
# config/default.yaml
llm:
  default_provider: openai
  max_tokens: 2000
  temperature: 0.7
  timeout: 30
  retry_attempts: 3

providers:
  openai:
    api_base: https://api.openai.com/v1
    models:
      chat: gpt-3.5-turbo
      completion: gpt-3.5-turbo-instruct
      embedding: text-embedding-3-small
  anthropic:
    api_base: https://api.anthropic.com
    models:
      chat: claude-2.1
      completion: claude-2.1
  mistral:
    api_base: https://api.mistral.ai/v1
    models:
      chat: mistral-tiny
      completion: mistral-tiny

prompts:
  system_role: |
    You are a helpful AI assistant focused on {{ domain }}.
    Respond in a {{ tone }} tone.
  task_format: |
    Given the following {{ input_type }}:
    {{ content }}
    {{ task_description }}
```

```yaml
# config/env/production.yaml
llm:
  max_tokens: 4000
  timeout: 60
  retry_attempts: 5

providers:
  openai:
    models:
      chat: gpt-4-turbo-preview
      completion: gpt-4-turbo-preview
  anthropic:
    models:
      chat: claude-3-opus
      completion: claude-3-opus
```

```yaml
# config/project/research.yaml
llm:
  default_provider: anthropic
  temperature: 0.2

prompts:
  system_role: |
    You are a research assistant specialized in {{ field }}.
    Focus on providing detailed, academic-style responses.
  
  paper_analysis: |
    Analyze the following research paper:
    {{ paper_content }}
    
    Provide:
    1. Key findings
    2. Methodology assessment
    3. Limitations
    4. Future research directions
```

```yaml
# ~/.config/myapp/local.yaml
llm:
  default_provider: mistral  # Use cheaper model for development
  max_tokens: 1000          # Limit tokens in development

providers:
  mistral:
    api_base: http://localhost:8000  # Local model server
    models:
      chat: mistral-small
      completion: mistral-small
```

### Advanced Usage

#### Merging Multiple Configurations

```python
from yamja import load_configs
import os

# Load and merge multiple configs (first has highest priority)
cfg = load_configs([
    "~/.config/myapp/local.yaml",          # Local development overrides
    "config/env/production.yaml",           # Production settings
    "config/project/research.yaml",         # Project specific settings
    "config/default.yaml",                 # Default values
])

# Resulting merged configuration:
# {
#     "llm": {
#         "default_provider": "mistral",    # from local.yaml
#         "max_tokens": 1000,               # from local.yaml
#         "temperature": 0.2,               # from research.yaml
#         "timeout": 60,                    # from production.yaml
#         "retry_attempts": 5               # from production.yaml
#     },
#     "providers": {
#         "openai": {
#             "api_base": "https://api.openai.com/v1",  # from default.yaml
#             "models": {
#                 "chat": "gpt-4-turbo-preview",        # from production.yaml
#                 "completion": "gpt-4-turbo-preview",   # from production.yaml
#                 "embedding": "text-embedding-3-small"  # from default.yaml
#             }
#         },
#         "anthropic": {
#             "api_base": "https://api.anthropic.com",  # from default.yaml
#             "models": {
#                 "chat": "claude-3-opus",              # from production.yaml
#                 "completion": "claude-3-opus"         # from production.yaml
#             }
#         },
#         "mistral": {
#             "api_base": "http://localhost:8000",      # from local.yaml
#             "models": {
#                 "chat": "mistral-small",              # from local.yaml
#                 "completion": "mistral-small"         # from local.yaml
#             }
#         }
#     },
#     "prompts": {
#         "system_role": "You are a research...",       # from research.yaml
#         "task_format": "Given the following...",      # from default.yaml
#         "paper_analysis": "Analyze the following..."  # from research.yaml
#     }
# }
```

## Configuration Merging Rules

1. For top-level dictionaries, keys are merged recursively
2. For lists and scalar values, later configurations override earlier ones
3. Include directives are processed depth-first
4. Local values take precedence over included values

## Requirements

- Python >= 3.13
- Jinja2 >= 3.1.4
- PyYAML >= 6.0.2

## License

MIT License - see [LICENSE](LICENSE) for details.

## Author

Created by Maciej Obarski

## Links

- [GitHub Repository](https://github.com/mobarski/yamja)
- [PyPI Package](https://pypi.org/project/yamja/) 