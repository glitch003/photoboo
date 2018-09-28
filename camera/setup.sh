!#/bin/bash
wget https://bootstrap.pypa.io/get-pip.py
python get-pip.py
wget "https://github.com/jabelone/OpenCV-for-Pi/raw/master/latest-OpenCV.deb"
apt-get update
apt-get upgrade
apt-get install build-essential cmake
apt-get install libgtk-3-dev
apt-get install libboost-all-dev

pip install numpy
pip install scipy
pip install scikit-image
pip install picamera
pip install pathlib2

apt-get install libtiff5-dev libjasper-dev libpng12-dev
apt-get install libjpeg-dev
apt-get install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
apt-get install libgtk2.0-dev
apt-get install libatlas-base-dev gfortran
apt-get install python-dev

pip install numpy

dpkg -i latest-OpenCV.deb

pip install dlib
