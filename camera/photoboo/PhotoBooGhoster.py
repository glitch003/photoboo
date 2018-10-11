from .FaceCropper import FaceCropper
import cv2
import numpy as np
from collections import OrderedDict


class PhotoBooGhoster(object):
    face_cropper = None

    def __init__(self):
        self.face_cropper = FaceCropper(in_verbose_mode = True)

    def load_photo(self, filename):
        image = self.face_cropper.open_image(filename, greyscale=True)
        return image

    def save_background(self, image):
        self.face_cropper.save_image("background.jpg", image)

    def does_face_exist(self, image):
        try:
            self.face_cropper.get_face_bounding_box(image)
            return True
        except:
            return False

    def ghost_face(self, image):
        face_landmarks = self.get_face_landmarks(image)
        face_shape = self.get_face_shape(image, face_landmarks)
        ghost_face = self.fill_in_mouth_and_eyes(image, face_landmarks)
        blurred_background = self.horizontal_blur(image)
        merged_image = self.merge_images(
            ghost_face,
            blurred_background,
            face_shape
        )
        return merged_image

    def get_face_landmarks(self, image):
        face_bounding_box = self.face_cropper.get_face_bounding_box(image)
        landmarks = self.face_cropper.get_face_landmarks(
            image,
            face_bounding_box
        )
        return landmarks

    def fill_in_mouth_and_eyes(self, image, face_landmarks, alpha=1.0):
        # modified from:
        # https://www.pyimagesearch.com/2017/04/10/detect-eyes-nose-lips-jaw-dlib-opencv-python/
        overlay = image.copy()
        output = image.copy()
        FACIAL_LANDMARKS_IDXS = OrderedDict([
            ("mouth", (48, 68)),
            ("right_eyebrow", (17, 22)),
            ("left_eyebrow", (22, 27)),
            ("right_eye", (36, 42)),
            ("left_eye", (42, 48)),
            ("nose", (27, 35)),
            ("jaw", (0, 17))
        ])
        for (i, name) in enumerate(FACIAL_LANDMARKS_IDXS.keys()):
            # grab the (x, y)-coordinates associated with the
            # face landmark
            (j, k) = FACIAL_LANDMARKS_IDXS[name]
            pts = np.array(face_landmarks[j:k])

            color = (0, 0, 0)
            # check if are supposed to draw the jawline
            if name == "mouth" or name == "left_eye" or name == "right_eye":
                hull = cv2.convexHull(pts)
                cv2.drawContours(overlay, [hull], -1, color, -1)

            cv2.addWeighted(overlay, alpha, output, 1 - alpha, 0, output)
        return output

    def get_face_shape(self, image, landmarks):
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

        if len(image.shape) == 2:
            width, height = image.shape
        else:
            width. height, channels = image.shape

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

    def horizontal_blur(self, image, size=15):
        # modified from:
        # https://www.packtpub.com/mapt/book/application_development/9781785283932/2/ch02lvl1sec21/motion-blur
        # generating the kernel
        if len(image.shape) == 2:
            width, height = image.shape
        else:
            width, height, channels = image.shape

        percent_blur = 5.0
        size = int(width * (percent_blur / 100.0))

        kernel_motion_blur = np.zeros((size, size))
        kernel_motion_blur[int((size-1)/2), :] = np.ones(size)
        kernel_motion_blur = kernel_motion_blur / size

        # applying the kernel to the input image
        output = cv2.filter2D(image, -1, kernel_motion_blur)
        return output

    def merge_images(self, face_image, background_image, face_shape):
        face_shape_points = face_shape["points"]
        min_x, min_y, max_x, max_y = face_shape["bounds"]
        pts = np.array(face_shape_points).astype(np.int)
        mask = 0 * np.ones(background_image.shape, background_image.dtype)
        cv2.fillPoly(mask, [pts], (255, 255, 255), 1)

        if len(face_image.shape) == 2:
            width, height = face_image.shape
            face_image = cv2.cvtColor(face_image, cv2.COLOR_GRAY2RGB)
            background_image = cv2.cvtColor(
                background_image,
                cv2.COLOR_GRAY2RGB
            )
        else:
            width, height, channels = face_image.shape
        center = (
            int(round(min_x + (max_x - min_x)/2)),
            int(round(min_y + (max_y - min_y)/2))
        )
        # print(mask.tolist())
        merged_image = cv2.seamlessClone(
            face_image,
            background_image,
            mask,
            center,
            cv2.MIXED_CLONE
        )
        return merged_image

    def save_image(self, image, filename):
        self.face_cropper.save_image(image, filename)
