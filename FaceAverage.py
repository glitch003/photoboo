import os
import cv2
import numpy as np
import math
import sys

class FaceAverage:

    def read_images(self, folder_path) :
        images = [];
        
        # Look at each image inside a folder
        for file_path in os.listdir(folder_path):
            if file_path.endswith(".jpg"):
                image = cv2.imread(os.path.join(folder_path, file_path));

                # Convert to floating point
                image = np.float32(image) / 255.0;
                images.append(image);

        return images;