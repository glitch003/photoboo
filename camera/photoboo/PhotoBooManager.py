import time
import os
import sys
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
        script_folder = os.path.dirname(os.path.realpath(sys.argv[0]))
        console.log(script_folder)
        tmp_image_filename = "original_{}.jpg".format(
            round(time.time())
        )
        tmp_image_filepath = self.images_folder / Path(tmp_image_filename)
        print(tmp_image_filepath)
        print(self.images_folder.exists())
        self.camera.capture(tmp_image_filepath)
        image = self.photo_boo.load_photo(tmp_image_filename)
        does_face_exist = self.photo_boo.does_face_exist(image)
        if does_face_exist is False:
            self.photo_boo.save_background(self.background_filename)
        else:
            self.photo_boo.get_face_shape(image)
            background = self.photo_boo.load_photo(
                self.images_folder / self.background_filename
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
            self.photo_boo.save_image(image, output_filepath)
