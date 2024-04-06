import json
import os

data_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
saved_baseline_file = os.path.join(data_folder, "baseline.data")
saved_baseline_smooth_file = os.path.join(data_folder, "smooth_baseline.data")
config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")


def load_config():
    """
    Loads configuration settings from a JSON file.

    Reads the configuration from a specified JSON file and returns it as a dictionary.

    Returns:
        dict: Configuration settings loaded from the JSON file.
    """
    
    with open(config_file) as in_file:
        config = json.load(in_file)
    return config
