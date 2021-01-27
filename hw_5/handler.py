import logging
import os
from urllib.parse import unquote

from utils import header_checker, header_maker, HTTP_request_parser, file_performer

logging.basicConfig(
    filename="requests.log",
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


class HTTPResponseMaker(object):
    __slots__ = ["GET", "HEAD", "POST", "URL", "root_dir"]

    def __init__(self, request_type, url=None, root_dir=None):
        self.GET = request_type if request_type == "GET" else None
        self.HEAD = request_type if request_type == "HEAD" else None
        self.POST = request_type if request_type == "POST" else None
        self.URL = url
        self.root_dir = root_dir

    def __call__(self):

        # this url is  very suspicious
        if "../" in self.URL:
            return header_maker("404 Not Found")

        try:
            parsed_url = URLPerformer(self.URL, root_dir=self.root_dir)
        except AttributeError:
            return header_maker("405 Method Not Allowed")

        url_status, file_type, file_length, file_content = parsed_url.url_performer()

        if self.GET:
            if url_status:
                logging.info("Request GET -  %s, Response 200 OK" % self.URL)

                header = header_maker("200 OK", file_length, file_type)

                full_response = header + file_content

                return full_response

            else:
                logging.error("Request GET -  %s, Response 404 Not Found" % self.URL)
                return header_maker("404 Not Found")

        elif self.HEAD:
            if url_status:
                logging.info("Request HEAD, Response 200 OK")
                return header_maker(
                    "200 OK", file_length, file_type, response_type="HEAD"
                )
            else:
                return header_maker("404 Not Found")

        elif self.POST:
            logging.info("Request POST, Response 403 Forbidden")
            return header_maker("403 Forbidden")

        else:
            logging.error("Request OTHER, 405 Method Not Allowed")
            return header_maker("405 Method Not Allowed")


class URLPerformer(object):
    ERROR_FILLER = False, "", "", ""

    def __init__(self, url, root_dir=None):
        self.URL = [url_part for url_part in url.split("/") if url_part != ""]
        self.url_dir = os.listdir(root_dir)
        self.isDir = True if url[-1] == "/" else False
        self.args = url.split("?")[-1] if len(url.split("?")) == 2 else None
        self.root_dir = "./DOCUMENT_ROOT" if root_dir is None else root_dir

    def qualified_path_gen(self):
        # Using unquote for  %70%61%67%65%2e%68%74%6d%6c -> page.html
        try:
            if self.args is None:

                path_to_file, file_name = (
                    self.root_dir + "/" + "/".join(self.URL[:-1]),
                    unquote(self.URL[-1]),
                )

            else:
                path_to_file, file_name = (
                    self.root_dir + "/" + "/".join(self.URL[:-1]),
                    unquote(self.URL[-1]),
                )
                file_name = file_name.split("?")[0]

            return path_to_file + "/" + file_name

        # this url is  very suspicious
        except IndexError:
            raise

    def url_performer(self):

        try:
            full_path = self.qualified_path_gen()

            # It is not a directory like /blabla/dir and not ARGS
            if not self.isDir and self.args is None:

                return file_performer(full_path)

            # It is not a directory like /blabla/dir and ARGS
            elif not self.isDir and self.args is not None:

                return file_performer(full_path)

            # It is  a directory like /blabla/dir
            elif self.isDir:

                try:
                    list_files = os.listdir(full_path)

                    if "index.html" in list_files:
                        full_patch_to_index = full_path + "/" + "index.html"
                        return file_performer(full_patch_to_index)

                    else:
                        return self.ERROR_FILLER

                # Suddenly - it is not a directory
                except NotADirectoryError:
                    return self.ERROR_FILLER

            # Did not find any dir or files
            else:
                return self.ERROR_FILLER

        except IndexError:
            return self.ERROR_FILLER

        except FileNotFoundError:
            return self.ERROR_FILLER


def HTTP_handler(package, root_dir):
    request = HTTP_request_parser(package)
    request_main = request["Request"]
    request_type, url, _ = header_checker(request_main)
    response = HTTPResponseMaker(request_type, url=url, root_dir=None)
    resp = response()

    return resp


