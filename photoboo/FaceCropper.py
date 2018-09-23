import cv
import numpy as np
import dlib
import os
import time
from __future__ import print_function
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

    def open_image(self, image_filename):
        image = cv2.imread(image_filename)
        return image

    def get_face_bounding_box(self, image):
        self.say("Finding bounding box for face in image... ", "")
        if os.path.isfile(self.face_data_filename) is False or \
                os.access(self.face_data_filename, os.R_OK) is False:
            raise Exception(
                """haarscade file, '{}' is not accessible.
                Download from opencv""".format(
                    self.face_data_filename
                )
            )
        face_cascade = cv2.CascadeClassifier(self.face_data_filename)
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
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
        self.say("Finding face landmarks landmarks... ", "")
        if os.path.isfile(self.predictor_path) is False or \
                os.access(self.predictor_path, os.R_OK) is False:
            raise Exception(
                """haarscade file, '{}' is not accessible.
                Download from opencv""".format(
                    self.shape_predictor_68_face_landmarks
                )
            )
        predictor = dlib.shape_predictor(self.predictor_path)
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
        self.say("Saving image to file... ", "")
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
