import json
import logging
import os
import signal
import sys
import time
import traceback

import pandas as pd

import config
from utils import init_stream, close_stream, get_volume, filtered_data, calculate_metrics


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


def main():
    """
    Main function to monitor microphone volume.
    """

    # Load Saved Data Metrics
    logger.info("Load Saved Data Metrics")
    with open(config.saved_metrics_data_file) as in_file:
        saved_metrics_data = json.load(in_file)
    number_of_records = saved_metrics_data["number_of_records"]
    saved_mean_volume = saved_metrics_data["mean_volume"]
    saved_std_volume = saved_metrics_data["std_volume"]
    saved_trend = saved_metrics_data["trend"]
    saved_corr = saved_metrics_data["corr"]

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

        # Check if volume_data size reaches {number_of_records}
        if len(volume_data) >= number_of_records:
            # Load DataFrame
            df = pd.DataFrame(volume_data)

            # Filter anomalies
            df, mean_volume, std_volume = filtered_data(df)

            # Calculate rate of change of volume over time (slope of linear regression)
            reg, trend, corr = calculate_metrics(df)

            # Compare metrics
            mean_calc = mean_volume - saved_mean_volume
            std_calc = std_volume - saved_std_volume
            trend_calc = abs(trend - saved_trend)
            corr_calc = abs(corr - saved_corr)
            if mean_calc < 0.8 and std_calc < 5 and trend_calc < 0.1 and corr_calc < 0.1:
                logging.info(f"{timestamp} | {volume} | {mean_calc} | {std_calc} | {trend_calc} | {corr_calc}")
                break

            # Remove the last entry
            volume_data.pop()

        # Shift all entries one position forward
        volume_data = volume_data + [{"timestamp": timestamp, "volume": volume}]

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
