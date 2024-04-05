import logging

import numpy as np
import pyaudio

import config

# Constants
global p, stream

# Load Config
config = config.load_config()
CHUNK_SIZE = config["CHUNK_SIZE"]
CHANNELS = config["CHANNELS"]
RATE = config["RATE"]


def init_stream():
    """
    Initialize PyAudio stream for audio input.
    """

    logging.info("Initializing PyAudio stream...")

    # Create a global PyAudio instance
    global p
    p = pyaudio.PyAudio()

    # Open a PyAudio stream with specified parameters
    global stream
    stream = p.open(format=pyaudio.paInt16, channels=config["CHANNELS"], rate=config["RATE"], input=True, frames_per_buffer=config["CHUNK_SIZE"])


def close_stream():
    """
    Close PyAudio stream.
    """

    logging.info("Closing PyAudio stream...")

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


def filtered_data(df):
    # Calculate mean and standard deviation of volume
    mean_volume = df['volume'].mean()
    std_volume = df['volume'].std()

    # Define a threshold for anomalies (e.g., 3 standard deviations from the mean)
    threshold = 10 * std_volume

    # Filter out anomalies
    filtered_df = df[abs(df['volume'] - mean_volume) < threshold]

    return filtered_df
