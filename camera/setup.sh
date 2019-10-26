#!/bin/bash

# use python3 for everything because there are prebuilt binaries for raspi <3

apt-get update

apt-get install -y build-essential cmake pkg-config libjpeg-dev libtiff5-dev libjasper-dev libpng-dev libavcodec-dev libavformat-dev libswscale-dev libv4l-dev libxvidcore-dev libx264-dev libfontconfig1-dev libcairo2-dev libgdk-pixbuf2.0-dev libpango1.0-dev libgtk2.0-dev libgtk-3-dev libatlas-base-dev gfortran python3-dev libqtgui4 libqtwebkit4 libqt4-test python3-pyqt5 libhdf5-dev libhdf5-serial-dev libhdf5-103  python3-opencv libqtgui4 libqtwebkit4 libqt4-test python3-pyqt5 libhdf5-dev libhdf5-serial-dev libhdf5-103 python3-dev


# then use python3 for evertyhing because it's faster with prebuilt wheels


pip3 install numpy scipy scikit-image picamera pathlib2 requests imutils dlib pynput opencv-contrib-python

# get dlib wheel manually
# wget "https://www.piwheels.org/simple/dlib/dlib-19.16.0-cp35-cp35m-linux_armv7l.whl#sha256=0a6794090544e725042214387130e56cdfe6fb212c02a226bfb05bdc8ac59a87"

# pip3 install dlib-19.16.0-cp35-cp35m-linux_armv7l.whl

# and that's it.  legacy install is below for reference.