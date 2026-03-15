import json

CONFIG_SAVE_FILE = "config_save.json"
CONFIG_TEXTURE_FILE = "config_texture.json"


def load_save_config() -> dict:
    """
    loads user config from a JSON file
    :return: dictionary or None if not found
    """
    try:
        with open(CONFIG_SAVE_FILE, "r")as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def load_texture_config() -> dict:
    """
    loads user config from a JSON file
    :return: dictionary or None if not found
    """
    try:
        with open(CONFIG_TEXTURE_FILE, "r")as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_config(data_dict: dict, nr: int) -> None:
    """
    saves a configuration to a local JSON file
    :param data_dict: dictionary of save data with keys being UI elements
    :param nr: used to control which json to save to
    :return: None
    """
    if nr <= 0:
        with open(CONFIG_SAVE_FILE, "w") as f:
            json.dump(data_dict, f, indent=4)
    if nr > 0:
        with open(CONFIG_TEXTURE_FILE, "w") as f:
            json.dump(data_dict, f, indent=4)
