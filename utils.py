import logging

import numpy as np
import pyaudio
from sklearn.linear_model import LinearRegression

import config

# Constants
global p, stream

# Load Config
saved_config = config.load_config()
CHUNK_SIZE = saved_config["CHUNK_SIZE"]
CHANNELS = saved_config["CHANNELS"]
RATE = saved_config["RATE"]


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
    stream = p.open(format=pyaudio.paInt16, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK_SIZE)


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
    """
    Filter data based on volume anomalies.

    This function calculates the mean and standard deviation of the volume data in the DataFrame (df).
    It then defines a threshold for anomalies (e.g., 10 times the standard deviation from the mean)
    and filters out data points where the volume deviates from the mean by more than the threshold.

    Parameters:
    df (pandas.DataFrame): Input DataFrame containing volume data.

    Returns:
    pandas.DataFrame: Filtered DataFrame containing data points where volume is within the threshold.
    float: Mean volume value.
    float: Standard deviation of volume values.
    """

    # Calculate mean and standard deviation of volume
    mean_volume = df['volume'].mean()
    std_volume = df['volume'].std()

    # Define a threshold for anomalies (e.g., 3 standard deviations from the mean)
    threshold = 10 * std_volume

    # Filter out anomalies
    filtered_df = df[abs(df['volume'] - mean_volume) < threshold]

    return filtered_df, mean_volume, std_volume


def calculate_metrics(df):
    """
    Calculate metrics related to volume data.

    This function calculates the rate of change of volume over time (slope of linear regression),
    correlation between timestamps and volumes, using the provided DataFrame (df).

    Parameters:
    df (pandas.DataFrame): Input DataFrame containing timestamp and volume data.

    Returns:
    sklearn.linear_model.LinearRegression: Linear regression model fitted to the data.
    float: Rate of change of volume over time (slope of linear regression).
    float: Correlation between timestamps and volumes.
    """

    # Calculate rate of change of volume over time (slope of linear regression)
    X = df['timestamp'].values.reshape(-1, 1)
    y = df['volume'].values.reshape(-1, 1)
    reg = LinearRegression().fit(X, y)
    trend = reg.coef_[0][0]

    # Calculate correlation between timestamps and volumes
    corr = df['timestamp'].corr(df['volume'])

    return reg, trend, corr
