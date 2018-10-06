#!/usr/bin/env python3
import sys
import pymysql
import datetime
from os import environ
from settings import settings
from http_server import HttpServer


http_server = HttpServer(environ, sys.stdin)
http_server.set_header("Access-Control-Allow-Methods", "GET, PUT, OPTIONS")

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
    method = http_server.get_method()
    if method == "OPTIONS":
        http_server.print_headers()

    elif method == "GET":
        # FIXME: figure out if user is trying to get a particular photo
        conn = connect_to_mysql()
        photo_manager = PhotoManager(conn)

        query_params = http_server.get_query_parameters()
        if "id" in query_params:
            if query_params["id"] == "random":
                try:
                    photo = photo_manager.get_random_photo()
                    http_server.set_status(200)
                    http_server.print_headers()
                    http_server.print_json(photo)
                except:
                    http_server.set_status(400)
                    http_server.print_headers()
                    http_server.print_content("")

            else:
                try:
                    photo = photo_manager.get_photo_by_id(query_params["id"])
                    http_server.set_status(200)
                    http_server.print_headers()
                    http_server.print_json(photo)
                except:
                    http_server.set_status(400)
                    http_server.print_headers()
                    http_server.print_content("")
        else:
            try:
                photos = photo_manager.get_metadata_for_all_photos()
                http_server.set_status(200)
                http_server.print_headers()
                http_server.print_json(photos)
            except:
                http_server.set_status(400)
                http_server.print_headers()
                http_server.print_content("")

        conn.close()

    elif method == "PUT":
        photo_manager = PhotoManager(conn)
        post_data = http_server.get_post_json()
        if "name" not in post_data or \
                "data" not in post_data:
            http_server.set_status(400)
            http_server.print_headers()
            http_server.print_content("")
        else:
            conn = connect_to_mysql()
            try:
                photo_manager.save_new_photo(post_data["name"], post_data["data"])
                http_server.set_status(201)
                http_server.print_headers()
                http_server.print_json(get_share_types(conn, cur))
            except:
                http_server.set_status(400)
                http_server.print_headers()
                http_server.print_content("")

            conn.close()

    else:
        http_server.set_status(405)
        http_server.print_headers()


run()