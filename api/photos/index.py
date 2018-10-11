#!/usr/bin/env python3
import sys
import pymysql
from os import environ
from settings import settings
from http_server import HttpServer
from photo_manager import PhotoManager

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
    f = open("/tmp/photo_api.log", "w+")
    f.write("Method: {}\n".format(method))
    f.write("Query: {}\n".format(http_server.get_query_string()))
    # f.write("Payload: {}\n".format(http_server.get_post_json()))
    f.write("===========================\n")
    f.close()

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
                photo = photo_manager.get_photo_by_id(query_params["id"])
                if len(photo) > 0:
                    http_server.set_status(200)
                    http_server.print_headers()
                    http_server.print_json(photo)
                else:
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
        post_data = http_server.get_post_json()

        f = open("/tmp/photo_api.log", "w+")
        f.write("post_data: {}".format(str(list(post_data.keys()))))
        f.close()
        if "name" not in post_data or \
                "data" not in post_data:
            http_server.set_status(400)
            http_server.print_headers()
            response = {}
            if "name" in post_data:
                response["name"] = post_data["name"]
            else:
                response["name"] = "false"
            if "data" in post_data:
                response["data"] = "true"
            else:
                response["data"] = "false"
            http_server.print_json(response)
            f = open("/tmp/photo_api.log", "w+")
            f.write("ERROR: name or data not found")
            f.close()
        else:
            conn = connect_to_mysql()
            photo_manager = PhotoManager(conn)
            try:
                photo_manager.save_new_photo(
                    post_data["name"],
                    post_data["data"]
                )
                http_server.set_status(201)
                http_server.print_headers()
                http_server.print_content("")
                f = open("/tmp/photo_api.log", "w+")
                f.write("inserted photo")
                f.close()
            except:
                http_server.set_status(400)
                http_server.print_headers()
                http_server.print_content("")
                f = open("/tmp/photo_api.log", "w+")
                f.write("ERROR: problem inserting")
                f.close()

            conn.close()

    else:
        http_server.set_status(405)
        http_server.print_headers()
        http_server.print_content(method)
        f = open("/tmp/photo_api.log", "w+")
        f.write("ERROR: method not allowed")
        f.close()


run()
