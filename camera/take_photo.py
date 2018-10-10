#!/usr/bin/env python
import time
import picamera
import requests
from time import sleep
import cv2
import base64


def upload_photo(image, filename):
    api_url = "https://20mission.org/photoboo/api/photos/"
    image_bytestring = cv2.imencode('.jpg', image)[1].tostring()
    payload = {
        "name": filename,
        "data": base64.encodestring(image_bytestring).decode("utf-8")
    }
    print("Uploading {} to {}".format(filename, api_url))
    response = requests.put(api_url, json=payload)
    print("done: response: {}".format(str(response.status_code)))


def display(image_data, title="", time_s=None):
        cv2.imshow(title, image_data)
        cv2.waitKey(0)
        if time_s is not None:
            time.sleep(time_s)
        cv2.destroyAllWindows()


camera = picamera.PiCamera()
camera.resolution = (800, 600)
camera.shutter_speed = 50000
camera.exposure_compensation = 25
camera.exposure_mode = "night"
camera.awb_mode = "off"
sleep(1)

filename = "test_{}.jpg".format(str(int(round(time.time()))))
camera.capture('/tmp/images/{}'.format(filename))
camera.close()
image = cv2.imread('/tmp/images/{}'.format(filename))
print("filename: {}".format(filename))
upload_photo(image, filename)
