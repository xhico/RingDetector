# Microphone Volume Monitor and Doorbell Detection

This Python script monitors the volume of audio input from a microphone and detects doorbell rings based on predefined thresholds. It utilizes the PyAudio library to capture audio input from the microphone.

## Installation

Before running the script, ensure you have Python installed on your system along with the required dependencies. You can install dependencies using pip:

1. Clone this repository:
   ```bash
   git clone https://github.com/xhico/RingDetector.git
   ```

2. Install dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```

## Usage

To use this script:

1. Clone the repository or download the script file.
2. Ensure your system has a microphone connected.
3. Run the script:
   ```bash
   python3 RingDetector.py
   ```

4. The script will start monitoring the microphone volume. Press Ctrl+C to exit.

## Functionality

### Constants

- `DEVICE`: Device ID of the microphone.
- `SIMILARITY_THRESHOLD`: Threshold for determining similarity between volume readings.
- `VOLUME`: Current Volume

### Functions

- `get_volume(indata, frames, time, status)`: Calculate the volume of audio data from the microphone stream.
- `check_similarity(data1, data2)`: Check the similarity between two sets of volume readings.
- `main()`: Main function to monitor microphone volume and detect doorbell rings.

### Main Functionality

The `main()` function continuously monitors the microphone volume. When the volume exceeds a certain threshold, indicating a doorbell ring, it logs a message. It continues to monitor until interrupted by the user.

## Logging

The script logs events and errors using the Python logging module. Log messages are written to both a log file (`RingDetector.log`) and the console.

## Author

This script was written by xhico. Feel free to reach out with any questions or feedback.

## License

This project is licensed under the Apache-2.0 License - see the [LICENSE](LICENSE) file for details.


