#!/bin/bash

# Newer, faster setup...  Start with this raspi image which has opencv already
# https://medium.com/@aadeshshah/pre-installed-and-pre-configured-raspbian-with-opencv-4-1-0-for-raspberry-pi-3-model-b-b-9c307b9a993a
# link is at bottom
# https://mega.nz/#!tGg3QaQS!nZuGcPtrfNS9L933MTME3qjIKH3uobs6odF4MgckdoA



# then use python3 for evertyhing because it's faster with prebuilt wheels


pip3 install numpy scipy scikit-image picamera pathlib2 requests imutils

# get dlib wheel manually
wget "https://www.piwheels.org/simple/dlib/dlib-19.16.0-cp35-cp35m-linux_armv7l.whl#sha256=0a6794090544e725042214387130e56cdfe6fb212c02a226bfb05bdc8ac59a87"

pip3 install dlib-19.16.0-cp35-cp35m-linux_armv7l.whl

# and that's it.  legacy install is below for reference.






# wget https://bootstrap.pypa.io/get-pip.py
# python get-pip.py
# wget "https://github.com/jabelone/OpenCV-for-Pi/raw/master/latest-OpenCV.deb"
# apt-get update
# apt-get upgrade -y
# apt-get install -y build-essential cmake
# apt-get install -y libgtk-3-dev
# apt-get install -y libboost-all-dev
# apt-get install -y python-dev

# pip install numpy
# pip install scipy
# pip install scikit-image
# pip install picamera
# pip install pathlib2
# pip install requests
# pip install imutils

# apt-get install -y libtiff5-dev libjasper-dev libpng12-dev
# apt-get install -y libjpeg-dev
# apt-get install -y libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
# apt-get install -y libgtk2.0-dev
# apt-get install -y libatlas-base-dev gfortran

# dpkg -i latest-OpenCV.deb

# pip install dlib


