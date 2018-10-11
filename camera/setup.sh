#!/bin/bash
wget https://bootstrap.pypa.io/get-pip.py
python get-pip.py
wget "https://github.com/jabelone/OpenCV-for-Pi/raw/master/latest-OpenCV.deb"
apt-get update
apt-get upgrade -y
apt-get install -y build-essential cmake
apt-get install -y libgtk-3-dev
apt-get install -y libboost-all-dev
apt-get install -y python-dev

pip install numpy
pip install scipy
pip install scikit-image
pip install picamera
pip install pathlib2
pip install requests
pip install imutils

apt-get install -y libtiff5-dev libjasper-dev libpng12-dev
apt-get install -y libjpeg-dev
apt-get install -y libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
apt-get install -y libgtk2.0-dev
apt-get install -y libatlas-base-dev gfortran

dpkg -i latest-OpenCV.deb

pip install dlib
