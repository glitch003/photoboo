from .FaceCropper import FaceCropper
import cv2
import numpy as np


class PhotoBoo(object):
    face_cropper = None

    def __init__(self):
        self.face_cropper = FaceCropper()

    def load_photo(self, filename):
        image = self.face_cropper.open_image(filename)
        return image

    def does_face_exist(self, image):
        try:
            self.face_cropper.get_face_bounding_box(image)
            return True
        except:
            return False

    def save_background(self, image):
        self.face_cropper.save_image("background.jpg", image)

    def get_face_shape(self, image):
        face_bounding_box = self.face_cropper.get_face_bounding_box(image)
        landmarks = self.face_cropper.get_face_landmarks(
            image,
            face_bounding_box
        )
        min_x = 999999
        min_y = 999999
        max_x = 0
        max_y = 0
        for landmark in landmarks:
            x, y = landmark
            min_x = min(x, min_x)
            min_y = min(y, min_y)
            max_x = max(x, max_x)
            max_y = max(y, max_y)
        width, height, channels = image.shape
        image_bounds = (0, 0, width, height)
        triangles = self.face_cropper.get_deluanay_triangles_from_landmarks(
            landmarks,
            image_bounds
        )
        for triangle in triangles:
            point1, point2, point3 = triangle
        deluanay_points = self.face_cropper.get_raw_points_from_deluanay_triangles(
            triangles
        )
        face_shape_indeces = self.face_cropper.get_face_shape_from_deluanay_trangles(
            deluanay_points
        )
        # last_index = 0
        counter = 0
        min_x = 999999
        min_y = 999999
        max_x = 0
        max_y = 0
        face_shape_points = []
        for index in face_shape_indeces:
            x, y = deluanay_points[index[0]]
            face_shape_points.append((x, y))
            if x < min_x:
                min_x = x
            if y < min_y:
                min_y = y
            if x > max_x:
                max_x = x
            if y > max_y:
                max_y = y
            if counter > 0:
                # last_index = index
                counter += 1
        face_bounds = (min_x, min_y, max_x, max_y)
        output = {
            "points": face_shape_points,
            "bounds": face_bounds
        }
        return output

    def replace_face_with_background(self, image, background, face_shape):
        face_shape_points = face_shape["points"]
        min_x, min_y, max_x, max_y = face_shape_points["bounds"]
        pts = np.array(face_shape_points).astype(np.int)
        mask = 0 * np.ones(background.shape, background.dtype)
        cv2.fillPoly(mask, [pts], (255, 255, 255), 1)
        width, height, channels = image.shape
        center = (
            int(round(min_x + (max_x - min_x)/2)),
            int(round(min_y + (max_y - min_y)/2))
        )
        merged_image = cv2.seamlessClone(
            background,
            image,
            mask,
            center,
            cv2.NORMAL_CLONE
        )
        return merged_image

    def save_image(self, image, filename):
        self.face_cropper.save_image(image, filename)
