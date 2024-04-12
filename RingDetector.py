import logging
import os
import signal
import sys
import traceback

import numpy as np

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

    # Initialize PyAudio stream for audio input.
    utils.init_stream()

    # Log the start of recording volume data
    logger.info("Analyzing Volume Data")

    # Record volume_data
    while True:
        data = np.frombuffer(utils.stream.read(utils.CHUNK_SIZE), dtype=np.int16)
        freqs, fft_data = utils.compute_fft(data, utils.RATE)
        peaks = utils.detect_peaks(fft_data, utils.PEAK_THRESHOLD)

        print(f"{len(peaks)} | {freqs[peaks[0]]}")
        if len(peaks) > 0 and freqs[peaks[0]] > utils.FREQ_THRESHOLD:
            print("Doorbell ring detected!")


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
