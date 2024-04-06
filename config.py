import json
import os

data_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
saved_baseline_file = os.path.join(data_folder, "baseline.csv")
saved_baseline_smooth_file = os.path.join(data_folder, "smooth_baseline.csv")
config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")


def load_config():
    with open(config_file) as in_file:
        config = json.load(in_file)
    return config
