import socket
import logger

class ControlConnection(object):

    def __init__(self):

        self.connected = False
        self.timeout = 2.0
        self.logger = logger.get_logger()

    def connect(self, host, port, timeout=2.0):

        self.logger.info("Connecting to control server on {}:{}".format(host, port))

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(timeout)

        try:
            self.socket.connect((host, port))
            self.connected = True

        except socket.timeout:
            self.logger.error("Connecting to control server on {}:{} timed out".format(host, port))
            self.connected = False

        return self.connected

    def diconnected(self):

        self.socket.close()
        self.connected = False

    def is_connected(self):

        return self.connected
