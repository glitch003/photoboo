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
    cur = conn.cursor()
    return conn, cur


def run():
    method = http_server.get_method()
    if method == "OPTIONS":
        http_server.print_headers()

    elif method == "GET":
    	# FIXME: figure out if user is trying to get a particular photo
        conn, cur = connect_to_mysql()
        query = "SELECT `id`,`name`,`ctime` from `photoboo_photos` ORDER BY `ctime` DESC;"
        cur.execute(query)

        PHOTO_ID = 0
        PHOTO_NAME = 1
        PHOTO_CTIME = 2

        photos = []

        for row in cur:
            photo = {
                "id": row[PHOTO_ID],
                "name": row[PHOTO_NAME],
                "ctime": int(row[PHOTO_CTIME].timestamp())
            }
            photos.append(photo)
        cur.close()
        conn.close()

        http_server.set_status(200)
        http_server.print_headers()
        http_server.print_json(photos)

   	elif method == "PUT":
        post_data = http_server.get_post_json()
        if "name" not in post_data or \
                "data" not in post_data:
            http_server.set_status(400)
            http_server.print_headers()
        else:
            conn, cur = connect_to_mysql()
            name = conn.escape(post_data["name"])
            data = conn.escape(post_data["data"])
            query = "INSERT INTO `photoboo_photos` (`name`,`data`) values ({},FROM_BASE64({}));".format(
                name,
                data
            )
            cur.execute(query)
            conn.commit()

            http_server.set_status(201)
            http_server.print_headers()
            http_server.print_json(get_share_types(conn, cur))
            conn.close()

        cur.close()
        conn.close()
    else:
        http_server.set_status(405)
        http_server.print_headers()


run()
