import time
import os
import sys
import base64
from .PhotoBooGhoster import PhotoBooGhoster
from datetime import datetime
import requests
import traceback
import cv2
import time
import dlib
from picamera.array import PiRGBArray
from PIL import Image
import threading
import numpy as np


try:
    from pathlib import Path
except (ImportError, AttributeError):
    from pathlib2 import Path
Path().expanduser()
try:
    from picamera import PiCamera
except (ImportError, AttributeError):
    pass


class PhotoBooManager(object):
    camera = None
    photo_boo_ghoster = None
    # images_folder = Path('/Users/chris/PhotoData')
    images_folder = Path('/home/pi/PhotoData')

    face_data_filename = "haarcascades/haarcascade_frontalface_default.xml"
    predictor_path = "shape_predictor_68_face_landmarks.dat"

    def __init__(self):
        print("loading predictor")
        predictor_path = self.__get_real_path() / self.predictor_path
        if os.path.isfile(predictor_path.as_posix()) is False or \
                os.access(predictor_path.as_posix(), os.R_OK) is False:
            raise Exception(
                """haarscade file, '{}' is not accessible.
                Download from opencv""".format(
                    self.predictor_path.as_posix()
                )
            )
        predictor = dlib.shape_predictor(predictor_path.as_posix())
        print("predictor loaded")

        self.photo_boo_ghoster = PhotoBooGhoster(predictor)



    def take_photo(self, camera, timestamp):


        # camera.resolution = (960, 540)
        # camera.shutter_speed = 50000
        # camera.exposure_compensation = 25
        # camera.exposure_mode = "night"
        # camera.awb_mode = "off"
        # time.sleep(2)

        # camera.capture(tmp_image_filepath.as_posix())

        # camera.close()
        # image = self.open_image(tmp_image_filepath.as_posix())
        # capture to ram
        rawCapture = PiRGBArray(camera, size=(1920,1080))
        camera.capture(rawCapture, format="rgb", resize=(1920,1080), use_video_port=True)
        image = rawCapture.array

        # pil_image = Image.fromarray(image)

        # return pil_image

        # save image on bg thread
        threading.Thread(target=self.save_image, args=(image, "original", timestamp, True)).start()

        return image

        # remove fisheye distortion
        # undistorted_image = self.photo_boo_ghoster.face_cropper.undo_fisheye(image)
        # self.photo_boo_ghoster.save_image(
        #     undistorted_image,
        #     tmp_image_filepath.as_posix()
        # )
        # return tmp_image_filepath.as_posix()

    def save_image(self, image, image_prefix, timestamp, convert_bgr_to_rgb=False):
        script_folder = self.__get_script_folder()
        images_folder = script_folder / self.images_folder
        tmp_image_filename = "{}_{}.jpg".format(
            image_prefix,
            timestamp
        )
        tmp_image_filepath = images_folder / Path(tmp_image_filename)
        try:
            self.__create_path_if_not_exists(images_folder)
        except OSError:
            print("Creation of the directory {} failed".format(
                images_folder.as_posix()
            ))
            raise SystemExit

        print("saving image to {}".format(tmp_image_filepath.as_posix()))

        if convert_bgr_to_rgb:
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        cv2.imwrite(tmp_image_filepath.as_posix(), image)

    def open_image(self, filename):
        image = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
        # image = self.photo_boo_ghoster.face_cropper.open_image(filename, greyscale=True)
        return image

    def ghostify(self, raw_image, timestamp):
        raw_image = cv2.cvtColor(raw_image, cv2.COLOR_RGB2GRAY)
        # raw_image = self.open_image(image_filepath)
        # print("opened image. image dimensions are {}".format((raw_image.shape[0],raw_image.shape[1])))
        # raw_rotated_image = self.photo_boo_ghoster.face_cropper.rotate(
        #     raw_image,
        #     angle_degrees=0
        # )
        image = self.photo_boo_ghoster.face_cropper.auto_adjust_levels(raw_image)
        output = {}
        print("checking if face exists")
        possible_face_bounding_boxes = self.photo_boo_ghoster.does_face_exist(image)

        ghosted_face = self.photo_boo_ghoster.ghost_faces(image, possible_face_bounding_boxes)

        # save image in background
        # save image on bg thread
        threading.Thread(target=self.save_image, args=(ghosted_face, "ghosted", timestamp, False)).start()

        return ghosted_face

        # output["data"] = image
        # if possible_face_bounding_boxes is False:
        #     output["data"] = image
        #     output["face_found"] = False
        # else:
        #     try:
        #         output_filepath = self.__take_photoboo_photo(image, timestamp, possible_face_bounding_boxes)
        #     except Exception as ex:
        #         print(traceback.format_exc())
        #         output_filepath = image_filepath
        #     image = self.open_image(Path(output_filepath).as_posix())
        #     output["data"] = image
        #     output["face_found"] = True
        #     output["path"] = output_filepath

        # # rotate image 90 degrees
        # #self.__upload_photo(image, Path(output["path"]).name)
        # print("Photo exists at ")
        # print(Path(output["path"]).name)

        # # base64_data = base64.encodestring(output["data"])
        # # self.say(base64_data)
        # self.say("Face Found: {}".format(str(output["face_found"])))
        # self.say("Path: {}".format(output["path"]))
        # return output

    def __create_path_if_not_exists(self, images_folder):
        does_folder_exist = self.images_folder.exists()
        if does_folder_exist is False:
            images_folder.mkdir()

    def __get_script_folder(self):
        return Path(os.path.dirname(os.path.realpath(sys.argv[0])))

    def to_seconds(self, date):
        return time.mktime(date.timetuple())

    def __take_photoboo_photo(self, image, timestamp, possible_face_bounding_boxes):
        ghosted_face = self.photo_boo_ghoster.ghost_faces(image, possible_face_bounding_boxes)
        output_filename = self.images_folder / Path(
            "ghosted_{}.jpg".format(timestamp)
        )
        self.photo_boo_ghoster.save_image(ghosted_face, output_filename.as_posix())

        return output_filename

    def __get_real_path(self):
        real_path = Path(
            os.path.dirname(os.path.realpath(__file__))
        )
        return real_path

    def __upload_photo(self, image, filename):
        api_url = "https://20mission.org/photoboo/api/photos/"
        image_bytestring = cv2.imencode('.jpg', image)[1].tostring()
        payload = {
            "name": filename,
            "data": base64.encodestring(image_bytestring).decode("utf-8")
        }
        self.say("Uploading {} to {}".format(filename, api_url))
        response = requests.put(api_url, json=payload)
        self.say("done: response: {}".format(str(response.status_code)))


    def say(self, message):
        print("[{}] {}".format(self.__class__.__name__, message))
