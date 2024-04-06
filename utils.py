import logging

import numpy as np
import pyaudio

import config

# Constants
global p, stream

# Load Config
saved_config = config.load_config()
CHUNK_SIZE = saved_config["CHUNK_SIZE"]
CHANNELS = saved_config["CHANNELS"]
RATE = saved_config["RATE"]
CORRELATION_COEFFICIENT_THRESHOLD = saved_config["CORRELATION_COEFFICIENT_THRESHOLD"]


def init_stream():
    """
    Initialize PyAudio stream for audio input.
    """

    logging.info("Initializing PyAudio stream")

    # Create a global PyAudio instance
    global p
    p = pyaudio.PyAudio()

    # Open a PyAudio stream with specified parameters
    global stream
    stream = p.open(format=pyaudio.paInt16, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK_SIZE)


def close_stream():
    """
    Close PyAudio stream.
    """

    logging.info("Closing PyAudio stream")

    # Stop / Close the PyAudio stream
    if stream.is_active():
        stream.stop_stream()
        stream.close()

    # Terminate the PyAudio instance
    p.terminate()


def get_volume():
    """
    Get current volume from the microphone.

    Returns:
        float: The mean absolute volume value.
    """

    # Start streaming audio from the microphone
    if stream.is_stopped():
        stream.start_stream()

    # Read audio data from the stream
    data = stream.read(CHUNK_SIZE, exception_on_overflow=True)

    # Convert the binary data into a numpy array of int16
    data = np.frombuffer(data, dtype=np.int16)

    # Calculate the mean absolute volume
    volume = np.abs(data).mean()

    # Stop streaming audio
    if stream.is_active():
        stream.stop_stream()

    return volume


def smooth_data(volume_data):
    """
    Smooths the volume data using a simple moving average.

    Args:
        volume_data (list): A list of dictionaries where each dictionary contains information about volume at different points in time.

    Returns:
        list: A list of dictionaries where each dictionary contains the smoothed volume data.
    """

    # Initialize an empty list to store smoothed data
    smoothed_data = []

    # Set the window size for the moving average
    window_size = 5

    # Iterate through each volume entry
    for i in range(len(volume_data)):
        # Determine the start and end index for the window
        start_index = max(0, i - window_size // 2)
        end_index = min(len(volume_data), i + window_size // 2 + 1)

        # Extract the window of volume values
        window = volume_data[start_index:end_index]

        # Calculate the average of the window
        average = sum(window) / len(window)

        # Append the smoothed data to the smoothed_data list
        smoothed_data.append(average)

    return smoothed_data
