#!/bin/bash

sudo apt install portaudio19-dev -y
sudo mv /home/pi/RingDetector/RingDetector.service /etc/systemd/system/ && sudo systemctl daemon-reload
python3 -m pip install -r /home/pi/RingDetector/requirements.txt --no-cache-dir
chmod +x -R /home/pi/RingDetector/*