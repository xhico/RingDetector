import logging
import os
import signal
import sys
import time
import traceback

from utils import init_stream, close_stream, get_volume


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

    # Initialize PyAudio stream for audio input.
    init_stream()

    logger.info("Monitoring microphone volume")
    while True:
        volume = get_volume()
        logger.info(volume)
        time.sleep(0.1)


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
        close_stream()
    except Exception as ex:
        logger.error(traceback.format_exc())
        close_stream()
    finally:
        logger.info("End")
