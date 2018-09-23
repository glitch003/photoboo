from datetime import datetime
from picamera import PiCamera


class Camera:
    camera = None

    def __init__(self):
        self.camera = PiCamera()

    def take_photo(self, filename):
        filename = "images/iamge_{}.jpg".format(
            round(datetime.now().timestamp())
        )
        camera.capture(filename)
        return filename
