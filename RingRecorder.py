import csv
import logging
import os
import time
import traceback

import config
from utils import init_stream, close_stream, get_volume, smooth_data


def main():
    """
    Main function to monitor microphone volume.
    """

    # Create data_folder
    os.makedirs(config.data_folder, exist_ok=True)

    # Initialize PyAudio stream for audio input.
    init_stream()

    # Log the start of recording volume data
    logger.info("Recording Volume Data | CTRL-C to stop")

    # Initialize an empty list to store volume data
    volume_data = []

    # Record volume data
    counter = 0
    while True:
        try:

            # Get the current volume
            volume = get_volume()

            # Log the current volume and timestamp
            logger.info(f"{counter} | Volume - {volume}")

            # Append timestamp and volume to the list
            volume_data.append({"counter": counter, "volume": volume})

            # Wait for X seconds before taking the next reading
            time.sleep(0.001)

            # Increase counter
            counter += 1
        except KeyboardInterrupt:
            logger.info("Stopping Recording")
            break

    # Log the end of recording and the number of data points recorded
    number_of_records = len(volume_data)
    logger.info(f"Recorded {number_of_records} points")

    # Smooth volume_data
    smoothed_data = smooth_data(volume_data)

    # Save volume_data
    with open(config.saved_baseline_file, "w", newline='') as out_file:
        writer = csv.DictWriter(out_file, fieldnames=["counter", "volume"])
        writer.writeheader()
        writer.writerows(volume_data)

    # Save volume_data
    with open(config.saved_baseline_smooth_file, "w", newline='') as out_file:
        writer = csv.DictWriter(out_file, fieldnames=["counter", "volume"])
        writer.writeheader()
        writer.writerows(smoothed_data)


if __name__ == "__main__":
    # Set Logging
    LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"{os.path.abspath(__file__).replace('.py', '.log')}")
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()])
    logger = logging.getLogger()

    logger.info("--------------------")

    try:
        main()
    except Exception as ex:
        logger.error(traceback.format_exc())
    finally:
        close_stream()
        logger.info("End")
