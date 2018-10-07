import json
from urllib import parse


class HttpServer:
    headers = {
        "Status": "200 OK",
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, GET, OPTIONS, DELETE, PUT",
        "Access-Control-Allow-Headers": "x-requested-with, Content-Type, origin, authorization, accept, client-security-token"
    }
    STATUS_CODES = {
        100: "Continue",
        101: "Switching Protocols",
        102: "Processing",
        103: "Early Hints",
        200: "OK",
        201: "Created",
        202: "Accepted",
        203: "Non-Authoritative Information",
        204: "No Content",
        205: "Reset Content",
        206: "Partial Content",
        207: "Multi-Status",
        208: "Already Reported",
        226: "IM Used",
        300: "Multiple Choices",
        301: "Moved Permanently",
        302: "Found",
        303: "See Other",
        304: "Not Modified",
        305: "Switch Proxy",
        307: "Temporary Redirect",
        308: "Permanent Redirect",
        400: "Bad Request",
        401: "Unauthorized",
        402: "Payment Required",
        403: "Forbidden",
        404: "Not Found",
        405: "Method Not Allowed",
        406: "Not Acceptable",
        407: "Proxy Authentication Required",
        408: "Request",
        409: "Conflict",
        410: "Gone",
        411: "Length Required",
        412: "Precondition Failed",
        413: "Payload Too Large",
        414: "URI Too Long",
        415: "Unnsupported Media Type",
        416: "Range Not Satisfiable",
        417: "Expectation Failed",

        500: "Internal Server Error",
        501: "Not Implemented",
        502: "Service Unavailable"
    }

    def __init__(self, environ, payload):
        self.environ = environ
        self.payload = payload

    def get_method(self):
        method = self.environ.get("REQUEST_METHOD")
        if method is None:
            method = "GET"
        else:
            method = method.upper()
        return method

    def get_query_string(self):
        query_string = self.environ.get("QUERY_STRING")
        return query_string

    def get_query_parameters(self):
        query_params = dict(parse.parse_qsl(
            self.get_query_string()
        ))
        return query_params

    def get_post_json(self):
        post_data = {}
        try:
            post_data = json.load(self.payload)
        except:
            pass
        return post_data

    def print_headers(self):
        for key, value in self.headers.items():
            print("{}: {}".format(key, value))
        print("")

    def print_json(self, data):
        print(json.dumps(data, indent=3))

    def print_content(self, data):
        print(data)

    def set_header(self, key, value):
        self.headers[key] = value

    def set_status(self, code):
        self.headers["Status"] = "{} {}".format(
            str(code), self.STATUS_CODES[code]
        )
