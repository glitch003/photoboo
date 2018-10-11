from __future__ import print_function
import cv2
import numpy as np
import dlib
import os
import time
try:
    from pathlib import Path
    Path().expanduser()
except (ImportError, AttributeError):
    from pathlib2 import Path
# Modified from from:
# http://gregblogs.com/computer-vision-cropping-faces-from-images-using-opencv2/


class FaceCropper(object):
    in_verbose_mode = False
    do_print_verbose_decorators = True

    face_data_filename = "haarcascades/haarcascade_frontalface_default.xml"
    predictor_path = "shape_predictor_68_face_landmarks.dat"
    color_white = (255, 255, 255)

    def __init__(self, in_verbose_mode=False):
        self.in_verbose_mode = in_verbose_mode
        self.say("In verbose mode")

    def __get_real_path(self):
        real_path = Path(
            os.path.dirname(os.path.realpath(__file__))
        )
        return real_path

    def open_image(self, image_filename, greyscale=False):
        if greyscale is True:
            image = cv2.imread(image_filename) # , cv2.IMREAD_GRAYSCALE)
        else:
            image = cv2.imread(image_filename)
        return image

    def undo_fisheye(self, image):
        # These values were derived from the calebrate_fisheye script
        DIM = (800, 600)
        K = np.array([
            [1047.0428993249554, 0.0, 409.3774656935277],
            [0.0, 1033.5648885354271, 249.71887499932328],
            [0.0, 0.0, 1.0]
        ])
        D = np.array([
            [-0.05410509676672891],
            [-8.036577386132445],
            [120.34638969712154],
            [-509.445110952727]
        ])

        width, height = image.shape[:2]
        map1, map2 = cv2.fisheye.initUndistortRectifyMap(
            K,
            D,
            np.eye(3),
            K,
            DIM,
            cv2.CV_16SC2
        )
        undistorted_image = cv2.remap(
            image,
            map1,
            map2,
            interpolation=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT
        )
        return undistorted_image

    def adjust_gamma(self, image, gamma=1.0):
        # taken from:
        # https://stackoverflow.com/a/51174313/9193553
        invGamma = 1.0 / gamma
        table = np.array([
            ((i / 255.0) ** invGamma) * 255
            for i in np.arange(0, 256)])
        return cv2.LUT(image.astype(np.uint8), table.astype(np.uint8))

    def auto_adjust_levels(self, image):
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4,4))
        adjusted_image = clahe.apply(image)
        return adjusted_image

    def rotate(self, image, angle_degrees=90):
        # modified from:
        # https://www.pyimagesearch.com/2017/01/02/rotate-images-correctly-with-opencv-and-python/
        # grab the dimensions of the image and then determine the
        # center
        height, width = image.shape[:2]
        center_x, center_y = (width // 2, height // 2)
     
        # grab the rotation matrix (applying the negative of the
        # angle to rotate clockwise), then grab the sine and cosine
        # (i.e., the rotation components of the matrix)
        M = cv2.getRotationMatrix2D((center_x, center_y), -angle_degrees, 1.0)
        cos = np.abs(M[0, 0])
        sin = np.abs(M[0, 1])
     
        # compute the new bounding dimensions of the image
        new_width = int((height * sin) + (width * cos))
        new_height = int((height * cos) + (width * sin))
     
        # adjust the rotation matrix to take into account translation
        M[0, 2] += (new_width / 2) - center_x
        M[1, 2] += (new_height / 2) - center_y
     
        # perform the actual rotation and return the image
        return cv2.warpAffine(image, M, (new_width, new_height))

    def get_face_bounding_box(self, image):
        face_data_path = self.__get_real_path() / self.face_data_filename
        self.say("Finding bounding box for face in image... ", "")
        if os.path.isfile(face_data_path.as_posix()) is False or \
                os.access(face_data_path.as_posix(), os.R_OK) is False:
            raise Exception(
                """haarscade file, '{}' is not accessible.
                Download from opencv""".format(
                    face_data_path
                )
            )
        face_cascade = cv2.CascadeClassifier(face_data_path.as_posix())
        try:
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        except:
            gray_image = image
        faces_bounding_box = face_cascade.detectMultiScale(
            gray_image,
            scaleFactor=1.05,
            minNeighbors=5,
            minSize=(100, 100),
            flags=cv2.CASCADE_SCALE_IMAGE
        )[0]
        self.say("done")
        return faces_bounding_box

    def get_face_landmarks(self, image, face_bounds=None):
        self.say("Finding face landmarks... ", "")
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
        if face_bounds is None:
            x = 0
            y = 0
            width = image.shape[0]
            height = image.shape[1]
        else:
            x = face_bounds[0]
            y = face_bounds[1]
            width = face_bounds[2]
            height = face_bounds[3]
        dlib_rect = dlib.rectangle(
            int(x),
            int(y),
            int(x + width),
            int(y + height)
        )
        detected_landmarks = predictor(image, dlib_rect).parts()
        landmarks = [
            (landmark.x, landmark.y) for landmark in detected_landmarks
        ]
        self.say("done")
        return landmarks

    def crop(self, image, bounding_box):
        self.say("Cropping image to bounds... ", "")
        x, y, width, height = [vector for vector in bounding_box]
        cropped_image = image[y:y+height, x:x+width]
        self.say("done")
        return cropped_image

    # Check if a point is inside a rectangle
    def __is_point_in_bounds(self, point, bounds):
        if point[0] < bounds[0]:
            return False
        elif point[1] < bounds[1]:
            return False
        elif point[0] > bounds[2]:
            return False
        elif point[1] > bounds[3]:
            return False
        return True

    def get_deluanay_triangles_from_landmarks(self, landmarks, bounds):
        self.say("Getting Deluanay triangles from landmarks... ", "")
        subdiv2d = cv2.Subdiv2D(bounds)
        for landmark in landmarks:
            x, y = landmark
            subdiv2d.insert((x, y))

        triangles = subdiv2d.getTriangleList()

        deluanay_triangles = []
        for triangle in triangles:
            x1, y1, x2, y2, x3, y3 = triangle
            point1 = (x1, y1)
            point2 = (x2, y2)
            point3 = (x3, y3)

            if self.__is_point_in_bounds(point1, bounds) and \
                    self.__is_point_in_bounds(point2, bounds) and \
                    self.__is_point_in_bounds(point3, bounds):
                deluanay_triangles.append((
                    point1,
                    point2,
                    point3
                ))
        self.say("done")
        return deluanay_triangles

    def get_raw_points_from_deluanay_triangles(self, deluanay_triangles):
        raw_points = []
        for triangle in deluanay_triangles:
            point1, point2, point3 = triangle
            raw_points.append(point1)
            raw_points.append(point2)
            raw_points.append(point3)
        return raw_points

    def get_face_shape_from_deluanay_trangles(self, raw_points):
        points = np.array(raw_points)
        hullIndex = cv2.convexHull(points, returnPoints=False)
        return hullIndex

    def save_image(self, image_data, output_filename):
        self.say("Saving image to file '{}'... ".format(output_filename), "")
        cv2.imwrite(output_filename, image_data)
        self.say("done")

    def say(self, message, end=None):
        if self.in_verbose_mode is True:
            if self.do_print_verbose_decorators is True:
                message = "[{}]: {}".format(self.__class__.__name__, message)
            if end is None:
                print(message)
                self.do_print_verbose_decorators = True
            else:
                print(message, end=end)
                self.do_print_verbose_decorators = False

    def display(self, image_data, title="", time_s=None):
        cv2.imshow(title, image_data)
        cv2.waitKey(0)
        if time_s is not None:
            time.sleep(time_s)
        cv2.destroyAllWindows()
