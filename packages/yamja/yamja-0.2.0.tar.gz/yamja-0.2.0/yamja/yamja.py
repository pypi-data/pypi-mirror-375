import os

import yaml
import jinja2


MAX_INCLUDE_DEPTH = 100


class Config:
    def __init__(self, data: dict):
        self.data = data
        loader = jinja2.DictLoader(self.lookup('templates', {}))
        self.jinja2_env = jinja2.Environment(loader=loader)

    def __repr__(self) -> str:
        return f'Config({self.data})'

    def lookup(self, key, default=..., env_var=None, cast=None) -> any:
        return lookup(self.data, key, default, env_var, cast)

    def render(self, key, **kwargs) -> str:
        text = self.lookup('templates.'+key)  # will raise KeyError if not found
        if 'macros' in self.data:
            macros_str = ''.join(self.data['macros'].values())
            self.data['templates']['macros'] = macros_str  # add macros to the loader
            header = "{% import 'macros' as macro %}"
            text = header + text
        template = self.jinja2_env.from_string(text)
        return template.render(**kwargs)


def load_config(path) -> Config:
    return _load_config(path, depth=0)


def _load_config(path, depth=0) -> Config:
    with open(path, 'r') as f:
        cfg = yaml.safe_load(f) or {}
    cfg = _handle_include(cfg, path, depth)
    return Config(cfg)


def _handle_include(cfg, path, depth=0):
    if depth > MAX_INCLUDE_DEPTH:
        raise ValueError(f'Include depth limit reached: {path}')
    if not isinstance(cfg, dict) or 'include' not in cfg:
        return cfg

    for include in cfg['include']:
        include_path = os.path.join(os.path.dirname(path), include)
        chunk = _load_config(include_path, depth+1).data
        if not isinstance(chunk, dict):
            continue
        # merge top level
        for k in cfg:
            # local values override included values
            if k != 'include':  # skip the include key itself
                if k not in chunk:
                    chunk[k] = cfg[k]
                elif isinstance(cfg[k], dict) and isinstance(chunk[k], dict):
                    # only update if both values are dictionaries
                    chunk[k].update(cfg[k])
                else:
                    # for non-dict values, local values override included values
                    chunk[k] = cfg[k]
        cfg = chunk

    if 'include' in cfg:
        del cfg['include']
    return cfg


def lookup(data, key, default=..., env_var=None, cast=None):
    """Look up a value in a nested data structure using dot notation.

    Args:
        data: The nested data structure to look up the value in.
        key: The dot-separated key path to look up.
        default: The value to return if the key is not found. If omitted
            or set to Ellipsis (...), a missing key raises KeyError. When
            provided together with `cast`, the default is also cast.
        env_var: Name of the environment variable to use as an override
            when present in os.environ (empty string allowed).
        cast: Callable to cast the resulting value (applied to env/config/default).

    Precedence: environment variable (if present) > config value > default.

    Notes:
        - Default is used only when the key is missing, not when the found value is falsy.
        - List indices in keys are supported, including negative indices.
    """

    if env_var and env_var in os.environ:
        value = os.getenv(env_var)
        return cast(value) if cast else value

    current = data
    for part in key.split('.'):
        try:
            # Handle both positive and negative indices
            if part.lstrip('-').isdigit():
                current = current[int(part)]
            elif hasattr(current, '__getitem__'):
                current = current[part]
            else:
                current = getattr(current, part)
        except (KeyError, IndexError, AttributeError, TypeError):
            if default is ...:
                raise KeyError(key)
            return cast(default) if cast else default
    return cast(current) if cast else current
