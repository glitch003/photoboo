import time
import os
import sys
import base64
from picamera import PiCamera
from .PhotoBoo import PhotoBoo
try:
    from pathlib import Path
    Path().expanduser()
except (ImportError,AttributeError):
    from pathlib2 import Path


class PhotoBooManager(object):
    camera = None
    photo_boo = None
    images_folder = Path("photoboo/images")
    background_filename = Path("background.jpg")

    def __init__(self):
        self.camera = PiCamera()
        self.photo_boo = PhotoBoo()

    def run(self):
        output = {}
        script_folder = self.__get_script_folder()
        images_folder = script_folder / self.images_folder
        tmp_image_filename = "original_{}.jpg".format(
            round(time.time())
        )
        tmp_image_filepath = images_folder / Path(tmp_image_filename)
        try:
            self.__create_path_if_not_exists(images_folder)
        except OSError:  
            print("Creation of the directory {} failed".format(
                images_folder.as_posix()
            ))
            raise SystemExit

        self.camera.capture(tmp_image_filepath.as_posix())
        image = self.photo_boo.load_photo(tmp_image_filepath.as_posix())
        does_face_exist = self.photo_boo.does_face_exist(image)

        output["data"] = image
        if does_face_exist is False:
            self.photo_boo.save_background(self.background_filename.as_posix())
            output["type"] = "background"
            output["path"] = self.background_filename
        else:
            output_filepath = self.__take_photoboo_photo(image, background)
            output["type"] = "face"
            output["path"] = output_filepath
            #self.__upload_photo(image, output["path"].name)

        return output
        base64_data = base64.encode(output["data"])
        self.say(base64_data)
        self.say("Type: {}".format(output["type"]))
        self.say("Path: {}".format(output["path"].as_posix()))

    def __create_path_if_not_exists(self, images_folder):
        does_folder_exist = self.images_folder.exists()
        if does_folder_exist is False:
            images_folder.mkdir()

    def __get_script_folder(self):
        return Path(os.path.dirname(os.path.realpath(sys.argv[0])))

    def __take_photoboo_photo(self, image, background):
        self.photo_boo.get_face_shape(image)
        background_filename = self.images_folder / self.background_filename
        background = self.photo_boo.load_photo(
            background_filename.as_posix()
        )
        self.photo_boo.replace_face_with_background(
            image, background
        )
        tmp_image_filename = self.images_folder / Path(
            "ghosted_{}.jpg".format(
                round(datetime.now().timestamp())
            )
        )
        output_filename = tmp_image_filename.replace("original", "ghosted")
        output_filepath = self.images_folder / Path(output_filename)
        self.photo_boo.save_image(image, output_filepath.as_posix())

        return outut_filepath

    def __upload_photo(self, image, filename):
        api_url = "http://20mission.org/photoboo/api/photo"
        method = "PUT"
        payload = {
            "name": filename,
            "data": base64.encode(image)
        }
        requests.put(api_url, json=payload)

    def say(self, message):
        print("[{}] {}".format(self.__class__.__name__, message))
