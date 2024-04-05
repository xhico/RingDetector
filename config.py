import json
import os

data_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
saved_metrics_data_file = os.path.join(data_folder, "saved_metrics.json")
config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")


def load_config():
    with open(config_file) as in_file:
        config = json.load(in_file)
    return config
