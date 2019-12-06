from .FaceCropper import FaceCropper
import cv2
import numpy as np
from collections import OrderedDict
import traceback


class PhotoBooPutFacesOnSnowmen(object):
    face_cropper = None
    snowman_face_coords = [
        [229, 556, 433, 722],
        [570, 339, 744, 492]
    ]

    def __init__(self, preloaded_predictor):
        self.face_cropper = FaceCropper(preloaded_predictor, in_verbose_mode = True)

    def load_photo(self, filename):
        image = self.face_cropper.open_image(filename, greyscale=True)
        return image

    def save_background(self, image):
        self.face_cropper.save_image("background.jpg", image)

    def does_face_exist(self, image):
        try:
            face_bounding_boxes = self.face_cropper.get_face_bounding_boxes(image)
            return face_bounding_boxes
        except Exception as ex:
            print(repr(ex))
            print(traceback.format_exc())
            return False

    def snowmanify_faces(self, image, face_bounding_boxes):
        # print("blurring image...")
        # background_image = self.horizontal_blur(image)
        background_image = cv2.imread('snow-background.jpg', cv2.IMREAD_COLOR)

        ghost_faces = []
        face_shapes = []

        i = 0
        for face_bounding_box in face_bounding_boxes:
            print("getting face stuff for index {}. face bounding box is {}".format(i, face_bounding_box))

            # crop image to face bounding box
            y = face_bounding_box[1]
            x = face_bounding_box[0]
            h = face_bounding_box[2]
            w = face_bounding_box[3]

            face_image = image[y:y+h, x:x+w]

            # scale image to snowman size
            min_snowman_x, min_snowman_y, max_snowman_x, max_snowman_y = self.snowman_face_coords[i]


            print("old face image shape: {}".format(face_image.shape))
            snowman_width = int(max_snowman_x - min_snowman_x)
            snowman_height = int(max_snowman_y - min_snowman_y)

            scale_percent = snowman_height / face_image.shape[0]
            width = int(face_image.shape[1] * scale_percent)
            height = int(face_image.shape[0] * scale_percent)

            dim = (width, height)
            face_image = cv2.resize(face_image, dim, interpolation = cv2.INTER_AREA)
            print("new face image shape: {}".format(face_image.shape))



            i += 1
            face_landmarks = self.face_cropper.get_face_landmarks(
                face_image,
                [0,0,h,w]
            )

            # print("face landmarks are {}.  getting face shape".format(face_landmarks))
            # sometimes the face shape detector fails.  lets just skip those faces.
            try:
                face_shape = self.get_face_shape(face_image, face_landmarks)
                # this can happen if we didn't get good triangles.  skip it.
                if face_shape == False:
                    continue
            except Exception as ex:
                print("Exception below is captured and handled...")
                print(traceback.format_exc())
                print("-------------------")
                continue
            # print("after exception, processing index ")
            # print(i)
            print("fill in mouth and eyes")
            ghost_face = self.fill_in_mouth_and_eyes(face_image, face_landmarks)

            face_shapes.append(face_shape)
            ghost_faces.append(ghost_face)

        print("merging images")
        merged_image = self.merge_images(
            ghost_faces,
            background_image,
            face_shapes
        )

        return merged_image


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

            # # # check if are supposed to draw the jawline
            if name == "left_eyebrow" or name == "left_eyebrow":
                hull = cv2.convexHull(pts)
                cv2.drawContours(overlay, [hull], -1, color, -1)

            color = (0, 165, 255)
            if name == "nose":
                hull = cv2.convexHull(pts)
                cv2.drawContours(overlay, [hull], -1, color, -1)

            cv2.addWeighted(overlay, alpha, output, 1 - alpha, 0, output)
        return output

    def get_face_shape(self, image, landmarks):
        # min_x = 999999
        # min_y = 999999
        # max_x = 0
        # max_y = 0
        # for landmark in landmarks:
        #     x, y = landmark
        #     min_x = min(x, min_x)
        #     min_y = min(y, min_y)
        #     max_x = max(x, max_x)
        #     max_y = max(y, max_y)

        if len(image.shape) == 2:
            height, width = image.shape
        else:
            height, width, channels = image.shape

        image_bounds = (0, 0, width, height)
        triangles = self.face_cropper.get_deluanay_triangles_from_landmarks(
            landmarks,
            image_bounds
        )

        # bail early if we didn't get any triangles
        if triangles == False:
            return False

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

    def translate(self, start, distance):
        return (np.array(start) + np.array(distance)).astype(np.int)


    def horizontal_blur(self, image, size=15):
        # modified from:
        # https://www.packtpub.com/mapt/book/application_development/9781785283932/2/ch02lvl1sec21/motion-blur
        # generating the kernel
        if len(image.shape) == 2:
            height, width = image.shape
        else:
            height, width, channels = image.shape

        percent_blur = 3.0
        size = int(width * (percent_blur / 100.0))

        kernel_motion_blur = np.zeros((size, size))
        kernel_motion_blur[int((size-1)/2), :] = np.ones(size)
        kernel_motion_blur = kernel_motion_blur / size

        # applying the kernel to the input image
        output = cv2.filter2D(image, -1, kernel_motion_blur)
        return output

    def merge_images(self, face_images, background_image, face_shapes):
        # merged_image = cv2.cvtColor(
        #             background_image,
        #             cv2.COLOR_GRAY2RGB
        #         )
        merged_image = background_image
        i = 0

        # print("face images has this many items")
        # print(len(face_images))
        # print("face shapes has this many items")
        # print(len(face_shapes))

        for face_image in face_images:
            print("****processing face images with index")
            print(i)

            face_shape = face_shapes[i]


            face_shape_points = face_shape["points"]
            min_x, min_y, max_x, max_y = face_shape["bounds"]

            # map to snowman face
            min_snowman_x, min_snowman_y, max_snowman_x, max_snowman_y = self.snowman_face_coords[i]

            # scale to snwoman x

            # print("face shape points: ")
            # print(face_shape_points)

            # print("old face image shape: {}".format(face_image.shape))
            # scale_percent = 60 # percent of original size
            # width = int(face_image.shape[1] * scale_percent / 100)
            # height = int(face_image.shape[0] * scale_percent / 100)

            # dim = (width, height)
            # # dim = ((max_snowman_x - min_snowman_x), (max_snowman_y - min_snowman_y))

            # face_image = cv2.resize(face_image, dim, interpolation = cv2.INTER_AREA)

            # print("new face image shape: {}".format(face_image.shape))
            # # face_shape_points

            snowman_center = (
                int(round(min_snowman_x + (max_snowman_x - min_snowman_x)/2)),
                int(round(min_snowman_y + (max_snowman_y - min_snowman_y)/2))
            )

            face_shape_center = (
                int(round(min_x + (max_x - min_x)/2)),
                int(round(min_y + (max_y - min_y)/2))
            )

            # shrink face_shape_points around face_shape_center



            # pts = self.translate(face_shape_points, [face_shape_center[0] - snowman_center[0], face_shape_center[1] - snowman_center[1]])
            pts = np.array(face_shape_points).astype(np.int)
            print("pts")
            print(pts)

            # pts = np.subtract(pts, np.array([100,100]))
            mask = np.zeros(face_image.shape, face_image.dtype)
            cv2.fillPoly(mask, [pts], (255, 255, 255))

            # mask = 255 * np.ones(face_image.shape, face_image.dtype)

            # print("checking len of face_image.shape")
            # print(len(face_image.shape))
            # print("checking len of merged_image.shape")
            # print(merged_image.shape)
            if len(face_image.shape) == 2:
                height, width = face_image.shape
                face_image = cv2.cvtColor(face_image, cv2.COLOR_GRAY2RGB)
                # merged_image = cv2.cvtColor(
                #     merged_image,
                #     cv2.COLOR_GRAY2RGB
                # )

            else:
                height, width, channels = face_image.shape



            center = (
                int(round(min_snowman_x + (max_snowman_x - min_snowman_x)/2)),
                int(round(min_snowman_y + (max_snowman_y - min_snowman_y)/2))
            )

            print("seamless cloning")
            # print(mask.tolist())
            merged_image = cv2.seamlessClone(
                face_image,
                merged_image,
                mask,
                center,
                cv2.NORMAL_CLONE # cv2.MIXED_CLONE
            )

            i += 1
        return merged_image

    def save_image(self, image, filename):
        self.face_cropper.save_image(image, filename)
