import time
import os
import sys
import base64
from .PhotoBooGhoster import PhotoBooGhoster
from datetime import datetime
import requests
import cv2
import time
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
    photo_boo = None
    images_folder = Path('/tmp/images') # Path("photoboo/images")
    background_filename = Path("background.jpg")

    def __init__(self):
        self.photo_boo = PhotoBooGhoster()

    def open_image(self, filename):
        self.say("Opening: {}".format(filename))
        image = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
        # image = self.photo_boo.face_cropper.open_image(filename, greyscale=True)
        return image

    def ghostify(self, image_filepath):
        raw_image = self.open_image(image_filepath)
        raw_rotated_image = raw_image
        raw_rotated_image = self.photo_boo.face_cropper.rotate(
            raw_image,
            angle_degrees=-90
        )
        image = self.photo_boo.face_cropper.auto_adjust_levels(raw_rotated_image)
        output = {}
        does_face_exist = self.photo_boo.does_face_exist(image)

        output["data"] = image
        if does_face_exist is False:
            output["data"] = image
            output["bytestring_data"] = cv2.imencode('.jpg', image)[1].tostring()
            output["face_found"] = False
            output["path"] = image_filepath
        else:
            try:
                output_filepath = self.__take_photoboo_photo(image)
            except:
                output_filepath = image_filepath
            image = self.open_image(output_filepath.as_posix())
            output["data"] = image
            output["bytestring_data"] = cv2.imencode('.jpg', image)[1].tostring()
            output["face_found"] = True
            output["path"] = output_filepath

        # self.__upload_photo(image, Path(output["path"]).name)
        self.say("Face Found: {}".format(str(output["face_found"])))
        self.say("Path: {}".format(output["path"]))
        return output

    def __create_path_if_not_exists(self, images_folder):
        does_folder_exist = self.images_folder.exists()
        if does_folder_exist is False:
            images_folder.mkdir()

    def __get_script_folder(self):
        return Path(os.path.dirname(os.path.realpath(sys.argv[0])))

    def to_seconds(self, date):
        return time.mktime(date.timetuple())

    def __take_photoboo_photo(self, image):
        ghosted_face = self.photo_boo.ghost_face(image)
        tmp_image_filename = self.images_folder / Path(
            "ghosted_{}.jpg".format(
                round(self.to_seconds(datetime.now()))
            )
        )
        output_filename = Path(tmp_image_filename.as_posix().replace(
            "original",
            "ghosted"
        ))
        output_filepath = Path(output_filename)
        self.photo_boo.save_image(ghosted_face, output_filepath.as_posix())

        return output_filepath

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

    def log(self, message):
        f = open("/tmp/photo_api.log", "w+")
        f.write(message)
        f.close()

    def say(self, message):
        complete_message = "[{}] {}".format(self.__class__.__name__, message)
        print(complete_message)
        self.log(complete_message)
