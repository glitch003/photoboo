#!/usr/bin/env python3
from FaceCropper import FaceCropper
import os
import sys
import cv2
import numpy as np


if __name__ == '__main__' :
    image_filename = sys.argv[1]
    save_filename = sys.argv[2]

    face_cropper = FaceCropper()

    image = face_cropper.open_image(image_filename)
    try:
        face_bounding_box = face_cropper.get_face_bounding_box(image)
        print(face_bounding_box)
    except:
        # set this as the background image
        print("background found!")


    sys.exit(1)
    '''
    x1, y1, x2, x2 = face_bounding_box
    center_x = x1 + (x2 - x1)/2
    center_y = y1 + (y2 - y1)/2
    vertical_axis = (x2 - x1)/2
    horizontal_axis = (y2 - y1)/2
    img = cv.ellipse(i
        mage,
        (center_x, center_y),
        (vertical_axis, horizontal_axis), 45, 130, 270, (255,255,255), 1)
    '''

    landmarks = face_cropper.get_face_landmarks(image, face_bounding_box)
    #print(landmarks)

    #for landmark in landmarks:
    #    cv2.circle(image, landmark, 5, (255, 0, 0), thickness=1, lineType=8, shift=0)
    
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

    face_bounds = (min_x, min_y, max_x, max_y)
    '''
    cv2.rectangle(
        image,
        (face_bounds[0], face_bounds[1]),
        (face_bounds[2], face_bounds[3]),
        (255, 0, 255),
        5
    )
    '''
    width, height, channels = image.shape
    image_bounds = (0, 0, width, height)
    #print(image_bounds)
    triangles = face_cropper.get_deluanay_triangles_from_landmarks(
        landmarks,
        image_bounds
    )
    #print("Triangles:")
    #print(triangles)
    for triangle in triangles:
        '''
        x1, y1, x2, y2, x3, y3 = triangle
        point1 = (x1, y1)
        point2 = (x2, y2)
        point3 = (x3, y3)
        '''
        point1, point2, point3 = triangle

    deluanay_points = face_cropper.get_raw_points_from_deluanay_triangles(
        triangles
    )
    face_shape_indeces = face_cropper.get_face_shape_from_deluanay_trangles(
        deluanay_points
    )

    last_index = 0
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
            '''
            cv2.line(
                image,
                deluanay_points[last_index[0]],
                deluanay_points[index[0]],
                (255, 255, 0),
                5
            )
            '''
        last_index = index
        counter += 1

    '''
    cv2.line(
        image,
        deluanay_points[face_shape_indeces[0][0]],
        deluanay_points[face_shape_indeces[len(face_shape_indeces)-1][0]],
        (255, 255, 0),
        5
    )
    '''

    pumpkin_image = face_cropper.open_image("beatles_inverted.jpg")
    pts = np.array(face_shape_points).astype(np.int)
    mask = 0 * np.ones(pumpkin_image.shape, pumpkin_image.dtype)
    cv2.fillPoly(mask, [pts], (255, 255, 255), 1)
    width, height, channels = image.shape
    center = (int(round(min_x + (max_x - min_x)/2)), int(round(min_y + (max_y - min_y)/2)))
    print(center)
    output = cv2.seamlessClone(pumpkin_image, image, mask, center,  cv2.NORMAL_CLONE)
    #for triangle in triangles:
    #    print(triangle)

    
    #face_cropper.draw_ellipse(face_bounding_box)
    #face_cropper.save_image(cropped_image, save_filename)

    cv2.imshow('image', output)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

