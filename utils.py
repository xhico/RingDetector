import logging

import numpy as np
import pyaudio

# Constants
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
SIMILARITY_THRESHOLD = 0.9
global p, stream


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
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK_SIZE)


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

    # Return True if correlation coefficient is above the threshold
    return correlation >= SIMILARITY_THRESHOLD
