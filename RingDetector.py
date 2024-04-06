import logging
import os
import signal
import sys
import time
import traceback
from collections import deque

import numpy as np

import config
import utils


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
        utils.close_stream()
        sys.exit(0)


signal.signal(signal.SIGTERM, signal_handler)


def main():
    """
    Main function to monitor microphone volume.
    """

    # Read Saved Smooth Baseline
    with open(config.saved_baseline_smooth_file) as in_file:
        saved_baseline_smooth = [float(volume) for volume in in_file.read().splitlines()]

    # Initialize PyAudio stream for audio input.
    utils.init_stream()

    # Initialize a rolling volume_data with a baseline with the same length of the saved baseline
    volume = utils.get_volume()
    volume_data = deque([volume for _ in range(len(saved_baseline_smooth))], maxlen=len(saved_baseline_smooth))

    # Log the start of recording volume data
    logger.info("Analyzing Volume Data")

    # Record volume_data
    counter = 0
    while True:
        # Get the current volume
        volume = utils.get_volume()

        # Append timestamp and volume to the list
        volume_data.append(volume)

        # Smooth volume_data
        volume_data_smooth = utils.smooth_data(list(volume_data))

        # Calculate correlation coefficient
        corr_coef = np.corrcoef(volume_data_smooth, saved_baseline_smooth)[0, 1]

        # Check if RING
        if corr_coef >= utils.CORRELATION_COEFFICIENT_THRESHOLD:
            logger.info(f"{volume} | {corr_coef}")
            with open(os.path.join(config.data_folder, f"tmp_{counter}.data"), "w") as out_file:
                out_file.writelines([str(volume) for volume in volume_data_smooth])
            counter += 1

        # Wait for X seconds before taking the next reading
        time.sleep(0.01)


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
