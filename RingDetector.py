import logging
import os
import time
import traceback

import numpy as np
import sounddevice as sd


def check_similarity(data1, data2, similarity_threshold=0.9):
    """
    Check the similarity between two sets of volume readings.

    Args:
    - data1 (list or numpy array): First set of volume readings.
    - data2 (list or numpy array): Second set of volume readings.
    - similarity_threshold (float): Threshold for similarity comparison.

    Returns:
    - bool: True if the datasets are similar, False otherwise.
    """
    # Convert data to numpy arrays if they are not already
    data1 = np.array(data1)
    data2 = np.array(data2)

    # Calculate Pearson correlation coefficient
    correlation = np.corrcoef(data1, data2)[0, 1]

    # Return True if correlation coefficient is above the threshold
    return correlation >= similarity_threshold


def get_volume(indata, frames, time, status):
    """
    Callback function to update the global VOLUME variable.

    Args:
    - indata (array): Input audio data.
    - frames (int): Number of frames.
    - time: Timestamp.
    - status: Status of the input stream.
    """

    global VOLUME
    VOLUME = np.abs(indata).mean()


def main():
    """
    Main function to monitor microphone volume and detect doorbell rings.
    """
    logger.info("Monitoring microphone volume")
    doorbell_rang = False
    while True:
        logger.info(VOLUME)

        # Check for doorbell ring
        if VOLUME > 50 and not doorbell_rang:
            logger.info("Doorbell Ring!")
            doorbell_rang = True
        elif VOLUME <= 20 and doorbell_rang:
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

    # Configuration
    DEVICE = "hw:2,0"
    SIMILARITY_THRESHOLD = 0.9
    VOLUME = 0.0

    # Open the audio stream
    logger.info("Open the audio stream")
    stream = sd.InputStream(callback=get_volume, channels=1, device=DEVICE)
    stream.start()

    try:
        main()
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt detected. Exiting...")
    except Exception as ex:
        logger.error(traceback.format_exc())
    finally:
        # Close the audio stream
        logger.info("Close the audio stream")
        stream.stop()
        stream.close()
        logger.info("End")
