import argparse
import datetime
import logging
import mimetypes
import os

logging.basicConfig(
    filename="requests.log",
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def HTTP_request_parser(http_request):
    OPT_FIELDS_NAMES = [
        "User-Agent",
        "Accept",
        "Cache-Control",
        "Host",
        "Accept-Encoding",
        "Accept-Language",
        "If-Modified-Since",
        "If-None_match",
        "Referer",
        "Connection",
        "Cookie",
        "Content-Length",
    ]

    http_response = http_request.decode("utf-8") if not None else ""
    http_response_parsed = http_response.split("\r\n")
    request_type, request_parameters = http_response_parsed[0], http_response_parsed[1:]

    request_dict = {"Request": request_type.split(" ")}

    for opt in request_parameters:
        try:
            opt_name, opt_value = opt.split(": ")

            if opt_name in OPT_FIELDS_NAMES:
                request_dict.update({opt_name: opt_value})

            else:
                pass

        except ValueError:
            pass

    return request_dict


def header_maker(status, content_length=None, content_type=None, response_type=None):
    response_status = "HTTP/1.0 %s\r\n" % status

    if response_type != "HEAD":
        """ Date, Server, Content-Length, Content-Type, Connection """
        date = "Date: %s\r\n" % datetime.datetime.now().strftime(
            "%a, %d %b %Y %H:%M:%S GMT"
        )
        content_length = (
            "Content-Length: %s\r\n" % content_length if content_length else ""
        )
        content_type = "Content-Type: %s\r\n" % content_type if content_type else ""
        connection = "Connection: close\r\n"
        server = "Server: My-Agenirider-HTTP-server\r\n\n"
        result_arr = [
            response_status,
            date,
            content_length,
            content_type,
            connection,
            server,
        ]

    else:
        result_arr = [response_status, "Content-Length: 38\r\n\r\n"]

    res = [ra.encode() for ra in result_arr]

    return b"".join(res)


def parse_args(args):
    arg_parser = argparse.ArgumentParser(description="Set specific parameters")
    arg_parser.add_argument("--r", type=str, help="Way to specific root dir")
    arg_parser.add_argument("--w", type=int, help="Quantity of workers")

    return arg_parser.parse_args(args)


def header_checker(header):
    try:
        request_type, url, _ = header
        return request_type, url, _
    except ValueError:
        return "TEST", "/", ""


def file_performer(full_path):

    EXIST_FILE_CONFIRMATION = b"bingo, you found it\n"

    try:
        file_size = os.path.getsize(full_path)

        correct_file_type, _ = mimetypes.guess_type(full_path.split("/")[-1])

        if correct_file_type is not None:

            with open(full_path, "rb") as file:
                file_content = file.read()

            return True, correct_file_type, file_size, file_content

        else:
            return True, "text/html", file_size, EXIST_FILE_CONFIRMATION
    except FileNotFoundError:
        logging.error("FILE NOT FOUND ERROR %s" % full_path)
        raise
