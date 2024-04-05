import json
import logging
import os
import signal
import sys
import time
import traceback

import pandas as pd
from sklearn.linear_model import LinearRegression

import config
from utils import init_stream, close_stream, get_volume, filtered_data

# Load Config
config = config.load_config()
CHUNK_SIZE = config["CHUNK_SIZE"]
CHANNELS = config["CHANNELS"]
RATE = config["RATE"]


def signal_handler(sig, frame):
    """
    Handle signals to gracefully terminate the script.

    Args:
        sig (int): The signal number.
        frame: Current stack frame object.

    Returns:
        None
    """

    if sig == signal.SIGTERM:
        logger.info("Script terminated by SIGTERM")
        close_stream()
        sys.exit(0)


signal.signal(signal.SIGTERM, signal_handler)


def analyze_doorbell_match(data, saved_data_metrics):
    # Load saved metrics
    saved_mean_volume = saved_data_metrics['mean_volume']
    saved_std_volume = saved_data_metrics['std_volume']
    saved_trend = saved_data_metrics['trend']
    saved_corr = saved_data_metrics['corr']

    # Load DataFrame
    df = pd.DataFrame(data)

    # Filter anomalies
    df = filtered_data(df)

    # Calculate mean and standard deviation of volume for both datasets
    mean_volume = df['volume'].mean()
    std_volume = df['volume'].std()

    # Calculate rate of change of volume over time (slope of linear regression)
    X = df['timestamp'].values.reshape(-1, 1)
    y = df['volume'].values.reshape(-1, 1)
    reg = LinearRegression().fit(X, y)
    trend = reg.coef_[0][0]

    # Calculate correlation between timestamps and volumes
    corr = df['timestamp'].corr(df['volume'])

    print(mean_volume)
    print(std_volume)
    print(trend)
    print(corr)

    # Compare metrics
    if (mean_volume - saved_mean_volume) < 0.5 and (std_volume - saved_std_volume) < 5 and (abs(trend - saved_trend) < 0.1) and (abs(corr - saved_corr) < 0.1):
        print("RING")
    else:
        print("NO RING")


def main():
    """
    Main function to monitor microphone volume.
    """

    # Load Saved Metrics
    data_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    saved_metrics_data_file = os.path.join(data_folder, "metrics.json")
    with open(saved_metrics_data_file, "r") as in_file:
        saved_data = json.load(in_file)

    # Initialize PyAudio stream for audio input.
    init_stream()

    # Log the start of recording volume data
    logger.info("Recording Volume Data")

    # Initialize an empty list to store volume data
    volume_data = []

    # Record volume
    while True:
        # Get the current timestamp
        timestamp = time.time_ns()

        # Get the current volume
        volume = get_volume()

        # Append timestamp and volume to the list
        volume_data.append({"timestamp": timestamp, "volume": volume})

        # Log the current volume and timestamp
        logger.info(f"Timestamp - {timestamp} | Volume - {volume}")

        # Wait for X seconds before taking the next reading
        time.sleep(0.001)


if __name__ == "__main__":
    # Set Logging
    LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"{os.path.abspath(__file__).replace('.py', '.log')}")
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()])
    logger = logging.getLogger()

    logger.info("--------------------")

    try:
        main()
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt detected. Exiting...")
    except Exception as ex:
        logger.error(traceback.format_exc())
    finally:
        logger.info("End")
