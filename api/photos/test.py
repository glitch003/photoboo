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
    http_server.set_status(200)
    http_server.print_headers()
    http_server.print_content(method)

    if method == "OPTIONS":
        http_server.print_headers()

    elif method == "GET":
        # FIXME: figure out if user is trying to get a particular photo
        print("GET!!!")
        conn = connect_to_mysql()
        photo_manager = PhotoManager(conn)

        query_params = http_server.get_query_parameters()
        http_server.set_status(200)
        http_server.print_headers()
        http_server.print_content(query_params)
        query_params = http_server.get_query_parameters()
        if "id" in query_params:
            if query_params["id"] == "random":
                photo = photo_manager.get_random_photo()
                http_server.set_status(200)
                http_server.print_headers()
                http_server.print_json(photo)

    elif method == "PUT":
        conn = connect_to_mysql()
        photo_manager = PhotoManager(conn)
        post_data = http_server.get_post_json()
        http_server.print_content(post_data)

        photo_manager.save_new_photo(
            post_data["name"],
            post_data["data"]
        )
        http_server.set_status(201)
        http_server.print_headers()
        http_server.print_content("")
        try:
            photo_manager.save_new_photo(
                post_data["name"],
                post_data["data"]
            )
            http_server.set_status(201)
            http_server.print_headers()
            http_server.print_content("")
        except:
            http_server.set_status(400)
            http_server.print_headers()
            http_server.print_content("")

        conn.close()

run()
