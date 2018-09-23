import cv2
import numpy as np
import dlib
import math
import os
import time
# taken from:
# http://gregblogs.com/computer-vision-cropping-faces-from-images-using-opencv2/


class FaceCropper:
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
        '''
        cv2.rectangle(
            image,
            (x, y),
            (x + width, y + height),
            self.color_white,
            2
        )
        '''
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
        '''
        landmarks = np.matrix(
            [[landmark.x, landmark.y] for landmark in detected_landmarks]
        )
        '''
        self.say("done")
        return landmarks

    def crop(self, image, bounding_box):
        self.say("Cropping image to bounds... ", "")
        x, y, width, height = [vector for vector in bounding_box]
        '''
        cv2.rectangle(
            image, (x, y), (x + width), (y + height), self.color_white
        )
        '''
        #cv2.rectangle(image, (x, y), (x + width, y + height), (255, 255, 255))

        cropped_image = image[y:y+height, x:x+width]
        self.say("done")
        return cropped_image

    # Check if a point is inside a rectangle
    def __is_point_in_bounds(self, point, bounds):
        if point[0] < bounds[0] :
            return False
        elif point[1] < bounds[1] :
            return False
        elif point[0] > bounds[2] :
            return False
        elif point[1] > bounds[3] :
            return False
        return True

    '''
    def get_deluanay_triangles_from_landmarks(self, landmarks, bounds):
        self.say("Getting Deluanay triangles from landmarks... ", "")
        subdiv2d = cv2.Subdiv2D(bounds)
        for landmark in landmarks:
            x, y = landmark
            subdiv2d.insert((x, y))

        triangles = subdiv2d.getTriangleList()
        return triangles
    '''

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
                '''
                deluanay_triangles.append((
                    x1, y1, x2, y2, x3, y3,
                ))
                '''
        return deluanay_triangles

        '''
        #print("subdv")
        deluanay_triangles = []
        for triangle in triangles:
            points = []
            x1, y1, x2, y2, x3, y3 = triangle

            point1 = (x1, y1)
            point2 = (x2, y2)
            point3 = (x3, y3)

            points.append(point1)
            points.append(point2)
            points.append(point3)

            if self.__is_point_in_bounds(point1, bounds) and \
                    self.__is_point_in_bounds(point2, bounds) and \
                    self.__is_point_in_bounds(point3, bounds):
                indeces = []
                for p0 in range(0, 3):
                    print("p0: " + str(p0))
                    num_points = len(points)
                    for p1 in range(0, num_points):
                        print(p1)
                        if (abs(points[p0][0] - landmarks[p1][0]) < 1.0 and \
                                abs(points[p0][1] - landmarks[p1][0]) < 1.0):
                            indeces.append(p1)
                    if len(indeces) == 3:
                        print("inceces are length 3")
                        deluanay_triangles.append((
                            indeces[0],
                            indeces[1],
                            indeces[3]
                        ))
            
        return deluanay_triangles
        '''

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
        hullIndex = cv2.convexHull(points, returnPoints = False)
        return hullIndex

    def __constrain_point(self, point, width, height):
        self.say("  Constraining point to new width and height... ", "")
        constrained_point = (
            min(
                max(point[0], 0),
                width - 1
            ),
            min(
                max(point[1], 0),
                height - 1
            )
        )
        self.say("done")
        return constrained_point

    def __get_similarity_transform(self, from_points, to_points):
        '''
        Compute similarity transform given two sets of two points.
        OpenCV requires 3 pairs of corresponding points.
        We are faking the third one.
        '''
        self.say("  Getting similarity transform between points... ", "")
        sin_60 = math.sin(60 * math.pi / 180)
        cosine_60 = math.cos(60 * math.pi / 180)

        from_points = np.copy(from_points).tolist()
        to_points = np.copy(to_points).tolist()

        from_x = cosine_60 * (
            from_points[0][0] - from_points[1][0]
        ) - sin_60 * (
            from_points[0][1] - from_points[1][1]
        ) + from_points[1][0]
        from_y = sin_60 * (
            from_points[0][0] - from_points[1][0]
        ) + cosine_60 * (
            from_points[0][1] - from_points[1][1]
        ) + from_points[1][1]

        from_points.append([np.int(from_x), np.int(from_y)])
        from_x = cosine_60 * (
            to_points[0][0] - to_points[1][0]
        ) - sin_60 * (
            to_points[0][1] - to_points[1][1]
        ) + to_points[1][0]
        from_y = sin_60 * (
            to_points[0][0] - to_points[1][0]
        ) + cosine_60 * (
            to_points[0][1] - to_points[1][1]
        ) + to_points[1][1]

        to_points.append([np.int(from_x), np.int(from_y)])
        transform = cv2.estimateRigidTransform(
            np.array([from_points]),
            np.array([to_points]),
            False
        )
        self.say("done")
        return transform

    def __apply_affine_transform(self, src, srcTri, dstTri, size):
        '''
        Apply affine transform calculated using srcTri and dstTri to src and
        output an image of size.
        '''
        self.say("  Applying Affine transform... ", "")
        # Given a pair of triangles, find the affine transform.
        warpMat = cv2.getAffineTransform(
            np.float32(srcTri),
            np.float32(dstTri)
        )
        # Apply the Affine Transform just found to the src image
        dst = cv2.warpAffine(
            src,
            warpMat,
            (size[0], size[1]),
            None,
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REFLECT_101
        )
        self.say("done")
        return dst

    def __warp_triangle(self, image_1, triangle_1, triangle_2):
        '''
        Warps and alpha blends triangular regions from img1 and img2 to img
        '''
        self.say("  Warping Deluanay Triangles between images... ", "")
        x = 0
        y = 1
        width = 3
        height = 4
        bounding_rectangle_1 = cv2.boundingRect(np.float32([triangle_1]))
        bounding_rectangle_2 = cv2.boundingRect(np.float32([triangle_2]))

        triangle_rectangle_1 = []
        triangle_rectangle_2 = []
        triangle_rectangle_2_int = []

        for point in range(0, 3):
            triangle_rectangle_1.append(
                (triangle_1[point][x] - bounding_rectangle_1[x]),
                (triangle_1[point][y] - bounding_rectangle_1[x])
            )
            triangle_rectangle_2.append(
                (triangle_2[point][x] - bounding_rectangle_2[x]),
                (triangle_2[point][y] - bounding_rectangle_2[x])
            )
            triangle_rectangle_2_int.append(
                (triangle_2[point][x] - bounding_rectangle_2[x]),
                (triangle_2[point][y] - bounding_rectangle_2[x])
            )

        mask = np.zeros(
            (bounding_rectangle_2[height], bounding_rectangle_2[width], 3),
            dtype=np.float32
        )
        cv2.fillConvexPoly(
            mask,
            np.int32(triangle_rectangle_2_int),
            (1.0, 1.0, 1.0),
            16,
            0
        )
        image_rectangle_1 = image_1[
            triangle_rectangle_1[y]:triangle_rectangle_1[y] +
            triangle_rectangle_1[height],
            triangle_rectangle_1[x]:triangle_rectangle_1[x] +
            triangle_rectangle_1[width]
        ]
        size = (bounding_rectangle_2[width], triangle_rectangle_1[height])
        image_rectangle_2 = self.__apply_affine_transform(
            image_rectangle_1,
            triangle_1,
            triangle_2,
            size
        )
        image_rectangle_2 = image_rectangle_2 * mask

        corrected_image = np.zeros((h, w, 3), np.float32())
        # Copy triangular region of the rectangular patch to the output image
        image_2[
            bounding_rectangle_2[y]:bounding_rectangle_2[y] +
            bounding_rectangle_2[height],
            bounding_rectangle_2[x]:bounding_rectangle_2[x] +
            bounding_rectangle_2[width]
        ] = image_2[
            bounding_rectangle_2[y]:bounding_rectangle_2[y] +
            bounding_rectangle_2[height],
            bounding_rectangle_2[x]:bounding_rectangle_2[x] +
            bounding_rectangle_2[width]
        ] * ((1.0, 1.0, 1.0) - mask)

        image_2[
            bounding_rectangle_2[y]:bounding_rectangle_2[y] +
            bounding_rectangle_2[height],
            bounding_rectangle_2[x]:bounding_rectangle_2[x] +
            bounding_rectangle_2[width]
        ] = image_2[
            bounding_rectangle_2[y]:bounding_rectangle_2[y] +
            bounding_rectangle_2[height],
            bounding_rectangle_2[x]:bounding_rectangle_2[x] +
            bounding_rectangle_2[width]
        ] + image_rectangle_2

        return image_2
        self.say("done")

    def average_faces(self, images):
        self.say("Averaging Faces... ")
        w = 600
        h = 600
        expected_eyecorner_distance = [
            (np.int(0.3 * w), np.int(h / 3)),
            (np.int(0.7 * w), np.int(h / 3))
        ]
        boundary_points = np.array(
            [
                (0, 0),
                (w/2, 0),
                (w-1, 0),
                (w-1, h/2),
                (w-1, h-1),
                (w/2, h-1),
                (0, h-1),
                (0, h/2)
            ]
        )

        all_normalized_landmarks = None

        normalized_images = []
        normalized_landmarks = []
        num_images = len(images)
        for image in images:
            image = np.float32(image) / 255.0
            self.display(image)
            landmark_points = self.get_face_landmarks(image)
            if all_normalized_landmarks is None:
                all_normalized_landmarks = np.array(
                    [(0, 0)] * (len(landmark_points) + len(boundary_points)),
                    np.float32()
                )
            eyecorner_source = [landmark_points[36], landmark_points[45]]
            face_skew_correction = self.__get_similarity_transform(
                eyecorner_source,
                expected_eyecorner_distance
            )
            normalized_image = cv2.warpAffine(
                image,
                face_skew_correction,
                (w, h)
            )
            eye_centered_landmarks = np.reshape(
                np.array(landmark_points),
                (68, 1, 2)
            )
            eye_normalized_landmarks = cv2.transform(
                eye_centered_landmarks,
                face_skew_correction
            )
            eye_normalized_landmarks = np.float32(
                np.reshape(eye_normalized_landmarks, (68, 2))
            )
            eye_normalized_landmarks = np.append(
                eye_normalized_landmarks,
                boundary_points,
                axis=0
            )
            all_normalized_landmarks = \
                (
                    all_normalized_landmarks + eye_normalized_landmarks
                ) / num_images
            normalized_images.append(normalized_image)
            normalized_landmarks.append(eye_normalized_landmarks)

        bounds = (0, 0, w, h)
        delaunay_triangles = self.get_deluanay_triangles_from_landmarks(
            all_normalized_landmarks,
            bounds
        )

        num_triangles = len(delaunay_triangles)
        average_image = np.zeros((h, w, 3), np.float32())
        for image_index in range(0, num_images):
            print("morphing image")
            #image = np.float32(image) / 255.0
            normalized_image = normalized_images[image_index]
            corrected_image = np.zeros((h, w, 3), np.float32())
            for triangle_index in range(0, num_triangles):
                delaunay_triangle = delaunay_triangles[triangle_index]
                triangle_from = []
                triangle_to = []

                for point in range(0, 3):
                    point_from = normalized_landmarks[
                        image_index
                    ]
                    point_from = normalized_landmarks[
                        image_index
                    ][delaunay_triangle[point]]
                    point_from = self.__constrain_point(point_from, w, h)
                    point_to = all_normalized_landmarks[
                        delaunay_triangle[point]
                    ]
                    point_to = self.__constrain_point(point_to, w, h)
                    triangle_from.append(point_from)
                    triangle_to.append(point_to)

                corrected_image = self.__warp_triangle(
                    normalized_image,
                    triangle_from,
                    triangle_to
                )
            self.display(corrected_image)
            average_image = \
                average_image + corrected_image

        average_image = average_image / num_images
        self.say("Done averaging faces")
        return average_image

    def crop_faces_from_file(self, image_filename, output_filename):
        self.say("Cropping faces from file...", "")
        if os.path.isfile(self.face_data_filename) is False or \
                os.access(self.face_data_filename, os.R_OK) is False:
            raise Exception(
                """haarscade file, '{}' is not accessible.
                Download from opencv""".format(
                    self.face_data_filename
                )
            )

        cascade = cv2.CascadeClassifier(self.face_data_filename)
        image = self.open_image(image_filename)

        image_dimensions = (image.shape[1], image.shape[0])
        image_frame = cv2.resize(image, image_dimensions)

        detected_faces = cascade.detectMultiScale(image_frame)

        color_white = (255, 255, 255)
        faces = []
        for face in detected_faces:
            x, y, width, height = [vector for vector in face]
            #cv2.rectangle(image, (x, y), (x+width, y+height), color_white)

            cropped_face_image = image[y:y+height, x:x+width]
            faces.append(cropped_face_image)
        self.say("done")
        return faces

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
