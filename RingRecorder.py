import logging
import os
import time
import traceback

import pandas as pd

from utils import load_config, init_stream, close_stream, get_volume


def main():
    """
    Main function to monitor microphone volume.
    """

    # Load Config
    load_config()

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

    # Convert volume_data to a DataFrame
    df = pd.DataFrame(volume_data)

    # Calculate mean and standard deviation of volume
    mean_volume = df['volume'].mean()
    std_volume = df['volume'].std()

    # Define a threshold for anomalies (e.g., 3 standard deviations from the mean)
    threshold = 10 * std_volume

    # Filter out anomalies
    filtered_df = df[abs(df['volume'] - mean_volume) < threshold]

    # Write filtered data to a CSV file
    filtered_volume_data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "volume_data.csv")
    filtered_df.to_csv(filtered_volume_data_file, index=False)


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
