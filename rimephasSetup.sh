#!/bin/bash

echo Installing Packages

# Start with uninstalling any preinstalled pygame packages
pip3 uninstall pygame

# GPIO
pip3 install RPi.GPIO

# Opencv
sudo apt-get install build-essential cmake pkg-config -y
sudo apt-get install libjpeg-dev libtiff5-dev libjasper-dev libpng-dev -y
sudo apt-get install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev -y
sudo apt-get install libxvidcore-dev libx264-dev -y
sudo apt-get install libfontconfig1-dev libcairo2-dev -y
sudo apt-get install libgdk-pixbuf2.0-dev libpango1.0-dev -y
sudo apt-get install libgtk2.0-dev libgtk-3-dev -y
sudo apt-get install libatlas-base-dev gfortran -y
sudo apt-get install libhdf5-dev libhdf5-serial-dev libhdf5-103 -y
sudo apt-get install libqtgui4 libqtwebkit4 libqt4-test python3-pyqt5 -y

pip3 install opencv-contrib-python==4.1.0.25

#Pyaudio
sudo apt-get install python-pyaudio python3-pyaudio sox libpcre3 libpcre3-dev libatlas-base-dev
pip3 install pyaudio

# Ledstrip
pip3 install adafruit-circuitpython-dotstar

# Google speech 
sudo apt-get install flac
pip3 install speechrecognition

# Pygame
pip3 install pygame==2.0.0.dev6
sudo apt-get install libsdl2-image-2.0-0

# Moviepy
pip3 install moviepy

# Matplotlib
pip3 install matplotlib
pip3 install mpld3

## Coral
echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | sudo tee /etc/apt/sources.list.d/coral-edgetpu.list
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
sudo apt-get update
sudo apt-get install libedgetpu1-std
pip3 install https://dl.google.com/coral/python/tflite_runtime-2.1.0.post1-cp37-cp37m-linux_armv7l.whl

sudo apt-get install python3-edgetpu

# Pillow
pip3 install Pillow

# Pushbullet for notifications
pip3 install pushbullet.py

pip3 install pydub

# Text to Speech
pip3 install gtts

# Clone all files from github
#mkdir rimephas
#cd rimephas
git clone https://github.com/Risskov/RIMEPHAS.git
#cd

# Fix audio
sudo cp RIMEPHAS/config.txt /boot/
sudo cp RIMEPHAS/.asoundrc ~/

