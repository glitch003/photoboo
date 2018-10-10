#!/usr/bin/env python
import time
import picamera
import requests
from time import sleep
from fractions import Fraction
import cv2
import base64
import numpy as np

def upload_photo(image, filename):
    api_url = "https://20mission.org/photoboo/api/photos/"
    image_bytestring = cv2.imencode('.jpg', image)[1].tostring()
    payload = {
        "name": filename,
        "data": base64.encodestring(image_bytestring).decode("utf-8")
    }
    print("Uploading {} to {}".format(filename, api_url))
    response = requests.put(api_url, json=payload)
    print("done: response: {}".format(str(response.status_code)))


'''
with picamera.PiCamera() as camera:
    camera.resolution = (1280, 720)
    camera.framerate = 30
    # Wait for the automatic gain control to settle
    time.sleep(2)
    # Now fix the values
    camera.shutter_speed = camera.exposure_speed
    camera.exposure_mode = 'off'
    g = camera.awb_gains
    camera.awb_mode = 'off'
    camera.awb_gains = g
    # Finally, take several photos with the fixed settings
    camera.capture_sequence(['image%02d.jpg' % i for i in range(10)])
'''


#with picamera.PiCamera() as camera:
camera = picamera.PiCamera()


#camera.resolution = (1280, 720)
camera.resolution = (800, 600)
# Set a framerate of 1/6fps, then set shutter
# speed to 6s and ISO to 800
#camera.framerate = Fraction(1, 1)
#camera.shutter_speed = 6000000
camera.shutter_speed = 50000
camera.exposure_compensation = 25
#camera.exposure_mode = 'off'
##camera.iso = 800
camera.exposure_mode = "night"
#camera.iso = 0
#camera.exposure_mode = "sports"
camera.awb_mode = "off"
# Give the camera a good long time to measure AWB
# (you may wish to use fixed AWB instead)
sleep(1)
# Finally, capture an image with a 6s exposure. Due
# to mode switching on the still port, this will take
# longer than 6 seconds
camera.capture('dark.jpg')
image = cv2.imread('dark.jpg', cv2.IMREAD_GRAYSCALE)
filename = "test_{}.jpg".format(str(int(round(time.time()))))
print("filename: {}".format(filename))
upload_photo(image, filename)


camera.close()



image = cv2.imread('adonis-moustache.jpg', cv2.IMREAD_GRAYSCALE)




def auto_contracts(image, gamma=1.0):
	histogram_size = 256
	alpha = 0.0
	beta = 0.0
	min_gray = 0
	max_gray = 0

	gray = np.zeros(image.shape, dtype=np.uint8)
	if (clip_histogram_percent == 0):
		min_val, max_val, min_loc, max_loc = max_cv2.minMaxLoc(gray)

	else:
		histogram = np.zeros(image.shape, dtype=np.uint8)

		range = [0, 256]
		histogram_range = range.copy()
		is_uniform = True
		accumulate = 0
		histogram = cv2.calcHist([image],[0], None, [256], [0, 256])

		accumulator = []
		accumulator[0] = histogram[0]
		for i in range(1, histogram_size):
			accumulator[i] = accumulator[i - 1] + histogram[i]

		max = accumulator[(len(accumulator)) - 1]


	invGamma = 1.0 / gamma
	table = np.array([
		((i / 255.0) ** invGamma) * 255
		for i in np.arange(0, 256)])
	return cv2.LUT(image.astype(np.uint8), table.astype(np.uint8))


void BrightnessAndContrastAuto(const cv::Mat &src, cv::Mat &dst, float clipHistPercent=0)
{

    CV_Assert(clipHistPercent >= 0);
    CV_Assert((src.type() == CV_8UC1) || (src.type() == CV_8UC3) || (src.type() == CV_8UC4));

    int histSize = 256;
    float alpha, beta;
    double minGray = 0, maxGray = 0;

    //to calculate grayscale histogram
    cv::Mat gray;
    if (src.type() == CV_8UC1) gray = src;
    else if (src.type() == CV_8UC3) cvtColor(src, gray, CV_BGR2GRAY);
    else if (src.type() == CV_8UC4) cvtColor(src, gray, CV_BGRA2GRAY);
    if (clipHistPercent == 0) {
        // keep full available range
        cv::minMaxLoc(gray, &minGray, &maxGray);
    } else {
        cv::Mat hist; //the grayscale histogram

        float range[] = { 0, 256 };
        const float* histRange = { range };
        bool uniform = true;
        bool accumulate = false;
        calcHist(&gray, 1, 0, cv::Mat (), hist, 1, &histSize, &histRange, uniform, accumulate);

        // calculate cumulative distribution from the histogram
        std::vector<float> accumulator(histSize);
        accumulator[0] = hist.at<float>(0);
        for (int i = 1; i < histSize; i++)
        {
            accumulator[i] = accumulator[i - 1] + hist.at<float>(i);
        }

        // locate points that cuts at required value
        float max = accumulator.back();
        clipHistPercent *= (max / 100.0); //make percent as absolute
        clipHistPercent /= 2.0; // left and right wings
        // locate left cut
        minGray = 0;
        while (accumulator[minGray] < clipHistPercent)
            minGray++;

        // locate right cut
        maxGray = histSize - 1;
        while (accumulator[maxGray] >= (max - clipHistPercent))
            maxGray--;
    }

    // current range
    float inputRange = maxGray - minGray;

    alpha = (histSize - 1) / inputRange;   // alpha expands current range to histsize range
    beta = -minGray * alpha;             // beta shifts current range so that minGray will go to 0

    // Apply brightness and contrast normalization
    // convertTo operates with saurate_cast
    src.convertTo(dst, -1, alpha, beta);

    // restore alpha channel from source 
    if (dst.type() == CV_8UC4) {
        int from_to[] = { 3, 3};
        cv::mixChannels(&src, 4, &dst,1, from_to, 1);
    }
    return;
}