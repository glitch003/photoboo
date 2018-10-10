#!/usr/bin/env python
import time
import picamera
import requests
from time import sleep
from fractions import Fraction


def upload_photo(image, filename):
    api_url = "https://20mission.org/photoboo/api/photos/"
    image_bytestring = cv2.imencode('.jpg', image)[1].tostring()
    payload = {
        "name": filename,
        "data": base64.encodestring(image_bytestring).decode("utf-8")
    }
    self.say("Uploading {} to {}".format(filename, api_url))
    response = requests.put(api_url, json=payload)
    self.say("done: response: {}".format(str(response.status_code)))


'''
with picamera.PiCamera() as camera:
    camera.resolution = (1280, 720)
    camera.framerate = 30
    # Wait for the automatic gain control to settle
    time.sleep(2)
    # Now fix the values
    camera.shutter_speed = camera.exposure_speed
    camera.exposure_mode = 'off'
    g = camera.awb_gains
    camera.awb_mode = 'off'
    camera.awb_gains = g
    # Finally, take several photos with the fixed settings
    camera.capture_sequence(['image%02d.jpg' % i for i in range(10)])
'''


with picamera.PiCamera() as camera:
    camera.resolution = (1280, 720)
    # Set a framerate of 1/6fps, then set shutter
    # speed to 6s and ISO to 800
    camera.framerate = Fraction(1, 6)
    camera.shutter_speed = 6000000
    camera.exposure_mode = 'off'
    camera.iso = 800
    # Give the camera a good long time to measure AWB
    # (you may wish to use fixed AWB instead)
    sleep(10)
    # Finally, capture an image with a 6s exposure. Due
    # to mode switching on the still port, this will take
    # longer than 6 seconds
    camera.capture('dark.jpg')
    image = cv2.imread('dark.jpg', cv2.IMREAD_GRAYSCALE)
    filename = "test_{}.jpg".format(str(int(round(time.time()))))
    upload_photo(image, filename)

