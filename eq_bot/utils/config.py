from typing import Any

from utils.file import read_yaml

# TODO: Move to configuration file
SECRETS_PATH="secrets.yaml"
CONFIG_PATH="config.yaml"


def _get_value_or_default(value, default_value):
    if value is None and default_value is not None:
        return default_value
    return value


def _get_from_path(input, path, default_value):
    if not input:
        return _get_value_or_default(None, default_value)

    current_dict = input
    key_parts = path.split('.')

    found_parent = False
    for key in key_parts[:-1]:
        if key not in current_dict:
            break
        current_dict = current_dict[key]
        found_parent = True

    value = None
    if found_parent:
        value = current_dict.get(key_parts[-1])
    
    return _get_value_or_default(value, default_value)


def get_secret(secret_path: str, default_value=None) -> Any:
    return _get_from_path(read_yaml(SECRETS_PATH, expect_found=False), secret_path, default_value)


def get_config(config_path: str, default_value=None) -> Any:
    return _get_from_path(read_yaml(CONFIG_PATH), config_path, default_value)
