import _thread as thread
import re
import socket
import sys

from handler import HTTP_handler
from utils import parse_args


class MainWorker(object):
    def __init__(self, host, port, args):
        self.root_dir = ""
        self.threads = []
        self.args = args
        self.port = port
        self.host = host
        self.default_workers = 5
        self.isWorking = True

    def handleClient(self, connection, root_dir):

        package = b""
        BUFFER_SIZE = 128
        END_OF_PACKET = b"\r\n\r\n"

        while True:
            try:
                chunk = connection.recv(BUFFER_SIZE)

                if not chunk:
                    break

                if len(re.findall(END_OF_PACKET, chunk)) == 1 or chunk == b"":
                    package += chunk
                    reply = HTTP_handler(package, root_dir)
                    connection.send(reply)
                    break

                else:
                    package += chunk

            except OSError:
                pass

        connection.close()

    def dispatcher(self):
        root_dir, workers = (
            self.args.r,
            self.args.w if self.args.w is not None else self.default_workers,
        )

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, self.port))
        server.listen(workers)

        while True:
            connection, address = server.accept()

            if self.isWorking:
                thread.start_new_thread(
                    self.handleClient,
                    (
                        connection,
                        root_dir,
                    ),
                )
            else:
                server.close()

    def stop_server(self):
        self.isWorking = False



def main(host="localhost", port=80):
    print("SERVER STARTED")
    try:
        args = parse_args(sys.argv[1:])
        MW = MainWorker(host, port, args)
        MW.dispatcher()

    except KeyboardInterrupt:
        MW.stop_server()
        print("SERVER STOPPED")


if __name__ == "__main__":
    main("localhost", 80)
