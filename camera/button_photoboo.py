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

    try:
        while True:
            if (GPIO.input(button_pin_id) == 1):
                image_filepath = command_arguments.image
                if image_filepath is None:
                    image_filepath = photo_boo.take_photo()

                image = photo_boo.ghostify(image_filepath)


if __name__ == "__main__":
    main()
