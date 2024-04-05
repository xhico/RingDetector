import json
import logging
import os
import time
import traceback

import pandas as pd

import config
from utils import init_stream, close_stream, filtered_data, get_volume, calculate_metrics

# Load Config
config = config.load_config()
CHUNK_SIZE = config["CHUNK_SIZE"]
CHANNELS = config["CHANNELS"]
RATE = config["RATE"]


def main():
    """
    Main function to monitor microphone volume.
    """

    # Create data_folder
    data_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    os.makedirs(data_folder, exist_ok=True)

    # Initialize PyAudio stream for audio input.
    init_stream()

    # Log the start of recording volume data
    logger.info("Recording Volume Data")

    # Initialize an empty list to store volume data
    volume_data = []

    # Record volume data for X seconds
    start_timestamp = time.time_ns()
    end_timestamp = start_timestamp + (4 * 1000000000)
    while time.time_ns() < end_timestamp:
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

    # Log the end of recording and the number of data points recorded
    logger.info(f"Recorded {len(volume_data)} points")

    # Load DataFrame
    df = pd.DataFrame(volume_data)

    # Filter anomalies
    df, mean_volume, std_volume = filtered_data(df)

    # Calculate rate of change of volume over time (slope of linear regression)
    reg, trend, corr = calculate_metrics(df)

    # Saved metrics
    metrics_data_file = os.path.join(data_folder, "saved_metrics.json")
    with open(metrics_data_file, "w") as out_file:
        metrics = {"mean_volume": mean_volume, "std_volume": std_volume, "trend": trend, "corr": corr}
        json.dump(metrics, out_file, indent=4)


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
        close_stream()
        logger.info("End")
