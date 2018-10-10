#!/usr/bin/env python
import argparse
from photoboo.PhotoBooManager import PhotoBooManager
import RPi.GPIO as GPIO

button_pin_id = 11

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


def setup_gpio_for_button(pin_id):
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(pin_id, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def main():
    setup_gpio_for_button(button_pin_id)

    command_parser = build_command_parser()
    command_arguments = command_parser.parse_args()

    photo_boo = PhotoBooManager()

    last_button_state = 0
    try:
        while True:
            current_button_state = GPIO.input(button_pin_id)
            if current_button_state != last_button_state:
                if (current_button_state == 1):
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
