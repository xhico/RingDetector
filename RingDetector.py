import logging
import os
import signal
import sys
import time
import traceback

import numpy as np
import pyaudio


def signal_handler(sig, frame):
    if sig == signal.SIGTERM:
        logger.info("Script terminated by SIGTERM")
        sys.exit(0)


signal.signal(signal.SIGTERM, signal_handler)


def initialize_stream():
    """
    Initialize PyAudio stream for microphone input.

    Returns:
        pyaudio.PyAudio: PyAudio object.
        pyaudio.Stream: PyAudio stream object.
    """

    # Initialize PyAudio and open stream for microphone input
    logger.info("Initialize PyAudio stream")
    _p = pyaudio.PyAudio()
    _stream = _p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK_SIZE)
    return _p, _stream


def close_stream():
    """
    Close PyAudio stream and terminate PyAudio.
    """

    # Stop && Close PyAudio stream and terminate PyAudio.
    logger.info("Closing the stream and terminate PyAudio")
    stream.stop_stream()
    stream.close()
    p.terminate()


def get_volume():
    """
    Calculate the volume of audio data from the microphone stream.

    Returns:
        float: The average volume of the audio data.
    """

    # Read audio data from the stream and calculate the average volume
    data = np.frombuffer(stream.read(CHUNK_SIZE, exception_on_overflow=False), dtype=VOLUME_DTYPE)
    volume = np.abs(data).mean()
    return volume


def check_similarity(data1, data2):
    """
    Check the similarity between two sets of volume readings.

    Args:
    - data1 (list or numpy array): First set of volume readings.
    - data2 (list or numpy array): Second set of volume readings.

    Returns:
    - bool: True if the datasets are similar, False otherwise.
    """

    # Convert data to numpy arrays if they are not already
    data1 = np.array(data1)
    data2 = np.array(data2)

    # Calculate Pearson correlation coefficient
    correlation = np.corrcoef(data1, data2)[0, 1]

    # Return correlation coefficient is above the threshold
    return correlation >= SIMILARITY_THRESHOLD


def main():
    """
    Main function to monitor microphone volume and detect doorbell rings.
    """

    logger.info("Monitoring microphone volume")
    doorbell_rang = False

    while True:

        # Get current volume level from the microphone stream
        volume = get_volume()

        # Check for doorbell ring
        if volume > 50 and not doorbell_rang:
            logger.info("Doorbell Ring!")
            doorbell_rang = True
        elif volume <= 20 and doorbell_rang:
            logger.info("Doorbell Stopped!")
            doorbell_rang = False

        # Sleep
        time.sleep(0.1)


if __name__ == "__main__":
    # Set Logging
    LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"{os.path.abspath(__file__).replace('.py', '.log')}")
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()])
    logger = logging.getLogger()

    logger.info("--------------------")

    # Constants
    CHUNK_SIZE = 2048
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    VOLUME_DTYPE = np.int16
    SIMILARITY_THRESHOLD = 0.9

    # Initialize PyAudio stream
    p, stream = initialize_stream()

    try:
        main()
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt detected. Exiting...")
    except Exception as ex:
        logger.error(traceback.format_exc())
    finally:
        close_stream()
        logger.info("End")
