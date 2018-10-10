#!/usr/bin/env python
import atexit
import argparse
from photoboo.PhotoBooManager import PhotoBooManager
import RPi.GPIO as GPIO

button_pin_id = 11
button_mode = GPIO.PUD_UP

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

def main():
    button_down = 1
    button_up = 0
    if button_mode == GPIO.PUD_UP:
        button_down = 0
        button_up = 1

    atexit.register(exit_handler)
    setup_gpio_for_button(button_pin_id, button_mode)

    command_parser = build_command_parser()
    command_arguments = command_parser.parse_args()

    photo_boo = PhotoBooManager()

    last_button_state = button_up
    try:
        while True:
            current_button_state = GPIO.input(button_pin_id)
            if current_button_state != last_button_state:
                if (current_button_state == button_down):
                    print("Button Down")
                    last_button_state
                    image_filepath = command_arguments.image
                    if image_filepath is None:
                        image_filepath = photo_boo.take_photo()

                    image = photo_boo.ghostify(image_filepath)
                else:
                    print("Button Up")

                last_button_state = current_button_state


    except:
        pass


if __name__ == "__main__":
    main()
