#!/usr/bin/env python3
from photo_manager import PhotoManager
import pymysql
from settings import settings
import base64


def connect_to_mysql():
    conn = pymysql.connect(
       host=settings["mysql"]["host"],
       port=settings["mysql"]["port"],
       user=settings["mysql"]["user"],
       passwd=settings["mysql"]["password"],
       db=settings["mysql"]["schema"],
       charset=settings["mysql"]["charset"],
       autocommit=True
    )
    return conn


def run():
    conn = connect_to_mysql()
    photo_manager = PhotoManager(conn)

    with open("/var/www/20mission.org/www/tmp/photos/ghosted_1539728519.0.jpg", "rb") as f:
        image = f.read()


    base64_image = base64.encodestring(image).decode("utf-8")

    post_data = {
        "name": "test.jpg",
        "data": base64_image
    }
    photo_manager.save_new_photo(
        post_data["name"],
        post_data["data"]
    )


run()