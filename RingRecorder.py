import logging
import os
import time
import traceback

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

    # Record volume data for 5 seconds
    start_time = time.time()
    while True:
        # Break the loop after 5 seconds
        if time.time() - start_time >= 5:
            break

        # Get the current volume
        volume = get_volume()

        # Append the volume to the list
        volume_data.append(volume)

        # Log the current volume
        logger.info(f"Volume - {volume}")

        # Wait for 0.1 seconds before taking the next reading
        time.sleep(0.1)

    # Log the end of recording and the number of data points recorded
    logger.info(f"Recorded {len(volume_data)} points")

    # Write Volume Data to file
    volume_data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "volume_data.data")
    with open(volume_data_file, "w") as out_file:
        out_file.writelines("\n".join(map(str, volume_data)))


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
