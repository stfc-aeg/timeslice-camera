import threading
import socket
import struct
import SocketServer
import subprocess
import time
import sched
import os

MCAST_GRP = '224.1.1.1'
MCAST_PORT = 5007

class CameraSim(object):

    def __init__(self):
        print "CameraSim __init__"

    def __enter__(self):
        print "CameraSim __enter__()", self
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print "CameraSim __exit__"

    def id(self):
        print "CameraSim id:", self


#class CameraServer(SocketServer.ThreadingMixIn, SocketServer.UDPServer):
class CameraServer(SocketServer.UDPServer):

    def __init__(self, camera, *args):

        SocketServer.UDPServer.__init__(self, *args)

        self.socket = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((MCAST_GRP, MCAST_PORT))
        mreq = struct.pack("4sl",
            socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)
        self.socket.setsockopt(
            socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        self.camera = camera

class UDPHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        cur_thread = threading.current_thread()
        print "{} : {} wrote: {}".format(cur_thread.name, self.client_address[0], data)
        self.server.camera.id()

if __name__ == '__main__':

    host, port = "127.0.0.1", 9999

    with CameraSim() as camera:
        server = CameraServer(camera, ("", 0), UDPHandler)
        server.serve_forever()
