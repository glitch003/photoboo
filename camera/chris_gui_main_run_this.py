#!/usr/bin/env python
import atexit
import argparse
from photoboo.PhotoBooManager import PhotoBooManager
import RPi.GPIO as GPIO
from picamera import PiCamera
import time
from pynput import keyboard, mouse
from PIL import Image
import threading
import cv2
import numpy as np
import sys

button_pin_id = 11
button_mode = GPIO.PUD_UP
# state 0 means waiting to take pic
# state 1 means processing
# state 2 means pic taken, and they are looking at the result
app_state = 0

camera = PiCamera(sensor_mode=2)
camera.hflip = True
camera.resolution = (1920, 1080)
camera.annotate_text = 'Press any key to get snowy'
camera.annotate_text_size = 60

orig_stdout = sys.stdout
f = open('/home/pi/stdlog.txt', 'a', 0)
sys.stdout = f

# consecutive_esc_presses = 0


photo_boo = PhotoBooManager()

main_overlay = 0



def build_command_parser():
    parser = argparse.ArgumentParser(
        description='Remove a face from a portrait'
    )
    parser.add_argument(
        '--image',
        help='use image file')
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Print debugging messages')
    return parser

def exit_handler():
    print("Exiting... cleaning up GPIO")
    GPIO.cleanup()

def setup_gpio_for_button(pin_id, button_mode):
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(pin_id, GPIO.IN, pull_up_down=button_mode)

def advance_state():
    global app_state
    print("advancing state.  current state is {}".format(app_state))
    if app_state == 0:
        app_state = 1
        print_timestamp("button pressed")
        threading.Thread(target=take_photo_and_process_image).start()
        # take_photo_and_process_image()
    elif app_state == 2:
        print_timestamp("remove ghost overlay")
        camera.remove_overlay(main_overlay)
        camera.annotate_text = 'Press any key to get snowy'
        app_state = 0


def print_timestamp(msg):
    print("[{}]: {}".format(round(time.time()), msg))

def take_photo_and_process_image():
    global main_overlay
    global app_state

    camera.annotate_text = ''

    timestamp = round(time.time())

    print_timestamp("snapping photo")

    image = photo_boo.take_photo(camera, timestamp)

    print_timestamp("add snap overlay")

    image_with_text = np.copy(image)
    cv2.putText(image_with_text, "Waiting for snow...", (700, 100), cv2.FONT_HERSHEY_SIMPLEX, 2.0, (255, 255, 255), lineType=cv2.LINE_AA)
    main_overlay = add_image_overlay(image_with_text)

    print_timestamp("ghostifying photo")
    image = photo_boo.snowmanify(image, timestamp)

    print_timestamp("remove snapped overlay")
    camera.remove_overlay(main_overlay)

    print_timestamp("add ghost overlay")

    cv2.putText(image, "Press any key to return to camera view", (500, 100), cv2.FONT_HERSHEY_SIMPLEX, 2.0, (255, 255, 255), lineType=cv2.LINE_AA)
    main_overlay = add_image_overlay(image)

    # done processing
    print_timestamp("setting app state to 2")
    app_state = 2

def add_image_overlay(raw_cv2_img):
    # Load the arbitrarily sized image
    # img = Image.open(image_filepath)
    # raw_cv2_img = cv2.cvtColor(raw_cv2_img, cv2.COLOR_BGR2RGB)

    img = Image.fromarray(raw_cv2_img)

    # Create an image padded to the required size with
    # mode 'RGB'
    pad = Image.new('RGB', (
        ((img.size[0] + 31) // 32) * 32,
        ((img.size[1] + 15) // 16) * 16,
        ))
    # Paste the original image into the padded one
    pad.paste(img, (0, 0))

    # Add the overlay with the padded image as the source,
    # but the original image's dimensions
    o = camera.add_overlay(pad.tobytes(), size=img.size)
    # By default, the overlay is in layer 0, beneath the
    # preview (which defaults to layer 2). Here we make
    # the new overlay semi-transparent, then move it above
    # the preview
    # o.alpha = 128
    o.layer = 3

    return o


def on_press(key):
    try:
        print('alphanumeric key {0} pressed'.format(
            key.char))
    except AttributeError:
        print('special key {0} pressed'.format(
            key))
    advance_state()

def on_release(key):
    print('{0} released'.format(
        key))
    # if key == keyboard.Key.esc:
        # Stop listener
        # return False

def on_click(x, y, button, pressed):
    if pressed:
        print('Mouse clicked at ({0}, {1}) with {2}'.format(x, y, button))
        advance_state()

def on_scroll(x, y, dx, dy):
    print('Mouse scrolled at ({0}, {1})({2}, {3})'.format(x, y, dx, dy))

def main():

    camera.start_preview()

    # Collect events until released
    mouseListener = mouse.Listener(on_click=on_click, on_scroll=on_scroll)
    mouseListener.start()
    with keyboard.Listener(
            on_press=on_press,
            on_release=on_release) as listener:
        listener.join()

    # clean up
    camera.close()
    f.close()

    # button_down = 1
    # button_up = 0
    # if button_mode == GPIO.PUD_UP:
    #     button_down = 0
    #     button_up = 1

    # atexit.register(exit_handler)
    # setup_gpio_for_button(button_pin_id, button_mode)

    # command_parser = build_command_parser()
    # command_arguments = command_parser.parse_args()

    # photo_boo = PhotoBooManager()

    # last_button_state = button_up
    # while True:
    #     current_button_state = GPIO.input(button_pin_id)
    #     if current_button_state != last_button_state:
    #         if (current_button_state == button_down):
    #             print("Button Down")
    #             last_button_state
    #             image_filepath = command_arguments.image
    #             if image_filepath is None:
    #                 image_filepath = photo_boo.take_photo()

    #             image = photo_boo.ghostify(image_filepath)
    #         else:
    #             print("Button Up")

    #         last_button_state = current_button_state



if __name__ == "__main__":
    main()
