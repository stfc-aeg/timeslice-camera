import threading
import socket
import struct
import SocketServer
import subprocess
import time
import sched
import os
import argparse

import camera_command_parser

MCAST_GRP = '224.1.1.1'
MCAST_PORT = 5007

class CameraSim(object):

    def __init__(self):
        print "Using simulated camera object"

    def __enter__(self):
        print "CameraSim __enter__()", self
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print "CameraSim __exit__"


class Camera(object):

    def __init__(self):
        print "Using real camera object"

    def __enter__(self):
        print "Camera __enter__()", self
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print "Camera __exit__"

#class CameraServer(SocketServer.ThreadingMixIn, SocketServer.UDPServer):
class CameraServer(SocketServer.UDPServer):

    def __init__(self, camera, args):

        SocketServer.UDPServer.__init__(self, ("", 0), UDPHandler)

        self.camera = camera
        self.id = args.id

        self.command_parser = camera_command_parser.CameraCommandParser(self.camera)

        self.socket = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((args.mcast_group, args.mcast_port))
        mreq = struct.pack("4sl",
            socket.inet_aton(args.mcast_group), socket.INADDR_ANY)
        self.socket.setsockopt(
            socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        print("Camera server starting up with ID {}".format(self.id))

class UDPHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        cur_thread = threading.current_thread()
        print "{} : {} wrote: {}".format(cur_thread.name, self.client_address[0], data)

        self.server.command_parser.parse_command(data)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Timeslice camera simulator")

    parser.add_argument('--id', action="store", dest="id", type=int, default=0,
                        help="Camera ID")
    parser.add_argument('--mcast_group', action="store", dest="mcast_group", default=MCAST_GRP,
                        help="Multicast group for camera server to bind to")
    parser.add_argument("--mcast_port", action="store", type=int, dest="mcast_port", default=MCAST_PORT,
                        help="Multicast port for camera server to bind to")
    parser.add_argument("--simulate", action="store_true", dest="simulate",
                        help="Use simulated camera bindings (debug feature)")
    args = parser.parse_args()

    if args.simulate:
        camera_type = CameraSim
    else:
        camera_type = Camera

    with camera_type() as camera:
        server = CameraServer(camera, args)
        server.serve_forever()
