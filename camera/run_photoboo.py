#!/usr/bin/env python
import argparse
from photoboo.PhotoBooManager import PhotoBooManager


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


def main():
    command_parser = build_command_parser()
    command_arguments = command_parser.parse_args()

    photo_boo = PhotoBooManager()
    image_filepath = command_arguments.image
    if image_filepath is None:
        image_filepath = photo_boo.take_photo()

    image = photo_boo.ghostify(image_filepath)


if __name__ == "__main__":
    main()
