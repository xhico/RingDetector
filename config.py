import json
import os


def load_config():
    config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
    with open(config_file) as in_file:
        config = json.load(in_file)
    return config
