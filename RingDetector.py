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

    # Log the start of recording volume data
    logger.info("Recording Volume Data")

    # Initialize volume_data with a baseline
    volume = utils.get_volume()
    volume_data = deque([volume for _ in range(len(saved_baseline_smooth))], maxlen=len(saved_baseline_smooth))

    # Record volume_data
    counter = len(volume_data)
    while True:
        # Get the current volume
        volume = utils.get_volume()

        # Log the current volume and timestamp
        logger.info(f"{counter} | Volume - {volume}")

        # Append timestamp and volume to the list
        volume_data.append(volume)

        # Smooth volume_data
        volume_data_smooth = utils.smooth_data(list(volume_data))

        # Calculate correlation coefficient
        corr_coef = np.corrcoef(volume_data_smooth, saved_baseline_smooth)[0, 1]
        if corr_coef >= utils.CORRELATION_COEFFICIENT_THRESHOLD:
            logger.info(f"RING | {corr_coef}")
            break

        # Wait for X seconds before taking the next reading
        time.sleep(0.001)

        # Increase counter
        counter += 1


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
