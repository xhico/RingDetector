import logging
import os
import time
import traceback

import config
import utils


def main():
    """
    Main function to monitor microphone volume.
    """

    # Create data_folder
    os.makedirs(config.data_folder, exist_ok=True)

    # Initialize PyAudio stream for audio input.
    utils.init_stream()

    # Log the start of recording volume data
    logger.info("Recording Volume Data | CTRL-C to stop")

    # Initialize an empty list to store volume data
    volume_data = []

    # Record volume data
    counter = 0
    while True:
        try:

            # Get the current volume
            volume = utils.get_volume()

            # Log the current volume and timestamp
            logger.info(f"Volume - {volume}")

            # Append timestamp and volume to the list
            volume_data.append(volume)

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
    smoothed_data = utils.smooth_data(volume_data)

    # Save baseline volume_data
    with open(config.saved_baseline_file, "w") as out_file:
        out_file.writelines([str(volume) for volume in volume_data])

    # Save smooth baseline volume_data
    with open(config.saved_baseline_smooth_file, "w") as out_file:
        out_file.writelines([str(volume) for volume in smoothed_data])


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
        utils.close_stream()
        logger.info("End")
