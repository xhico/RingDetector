import logging

import numpy as np
import pyaudio
from scipy.signal import find_peaks

import config

# Constants
global p, stream

# Load Config
saved_config = config.load_config()
CHUNK_SIZE = saved_config["CHUNK_SIZE"]
CHANNELS = saved_config["CHANNELS"]
RATE = saved_config["RATE"]
PEAK_THRESHOLD = saved_config["PEAK_THRESHOLD"]
FREQ_THRESHOLD = saved_config["FREQ_THRESHOLD"]


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


def detect_peaks(audio_data, threshold):
    peaks, _ = find_peaks(audio_data, height=threshold)
    return peaks


def compute_fft(data, rate):
    fft_data = np.fft.fft(data)
    freqs = np.fft.fftfreq(len(data), 1 / rate)
    return freqs[:len(freqs) // 2], np.abs(fft_data)[:len(fft_data) // 2]
