import socket
import errno
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

    def send(self, data):

        try:
            self.socket.sendall(data)
        except socket.error, e:
           if isinstance(e.args, tuple):
               if e[0] == errno.EPIPE:
                   # remote peer disconnected
                   self.logger.info("Control server connection closed by peer")
                   self.disconnect()
               else:
                   self.logger.error("Control server socket error: {}".format(e))
           else:
               self.logger.error("Control server socket error: {}".format(e))

    def disconnect(self):

        self.socket.close()
        self.connected = False

    def is_connected(self):

        return self.connected