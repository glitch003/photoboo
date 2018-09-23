#!/usr/bin/env python3
import argparse
from photoboo.PhotoBooManager import PhotoBooManager


def build_command_parser():
    parser = argparse.ArgumentParser(
        description='Remove a face from a portrait'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Print debugging messages')

    return parser


def main():
    command_parser = build_command_parser()
    command_arguments = command_parser.parse_args()
    print(command_arguments)

    photo_boo = PhotoBooManager()
    photo_boo.run()


if __name__ == "__main__":
    main()
