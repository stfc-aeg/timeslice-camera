import threading
import socket
import struct
import SocketServer
import subprocess
import time
import sched
import os
import argparse
import importlib
import io
import struct
import sys
import signal

import logger
import camera_command_parser
import control_connection
import led_driver
from led_driver import LedDriver

MCAST_GRP = '224.1.1.1'
MCAST_PORT = 5007

#class CameraServer(SocketServer.ThreadingMixIn, SocketServer.UDPServer):
class CameraServer(SocketServer.UDPServer):

    def __init__(self, args):

        SocketServer.UDPServer.__init__(self, ("", 0), UDPHandler)

        if args.simulate:
            self.camera_mod = importlib.import_module('simcamera')
            self.camera_type = self.camera_mod.SimCamera
            self.camera_mod.SimCamera.set_camera_id(args.id)
        else:
            self.camera_mod = importlib.import_module('picamera')
            self.camera_type = self.camera_mod.PiCamera
            
        # Initialise LED driver
        self.led = led_driver.LedDriver(args.simulate)
        self.led.set_colour(LedDriver.YELLOW)
        
        self.logger = logger.get_logger()

        self.id = args.id

        self.command_parser = camera_command_parser.CameraCommandParser(self)

        self.socket = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((args.mcast_group, args.mcast_port))
        mreq = struct.pack("4sl",
            socket.inet_aton(args.mcast_group), socket.INADDR_ANY)
        self.socket.setsockopt(
            socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        self.client_connected = False
        self.control_connection = control_connection.ControlConnection(self)

        self.image_io = io.BytesIO()

        self.version_hash, self.version_time = get_version()
        
        self.camera_params = {
            'resolution'    : [ (1920,1080), lambda val_str : tuple([int(val) for val in val_str.split('x')]) ],
            'framerate'     : [ 30, lambda val_str: int(val_str)],
            'shutter_speed' : [ 3000, lambda val_str: int(val_str) ],
            'iso'           : [ 800, lambda val_str: int(val_str) ],
            'exposure_mode' : [ 'fixedfps', lambda val_str: val_str ], 
            'color_effects' : [ None, lambda val_str: None if val_str == 'None' else tuple([int(val) for val in val_str.split('')]) ],
            'contrast'      : [ 0, lambda val_str: int(val_str) ],
            'drc_strength'  : [ 'off', lambda val_str: val_str ],
            'awb_mode'      : [ 'off', lambda val_str: val_str ],
            'awb_gains'     : [ (1.5, 1.5), lambda val_str : tuple([float(val) for val in val_str.split(',')]) ],
            'brightness'    : [ 50, lambda val_str: int(val_str) ],
        }

        # Install a signal handler
        signal.signal(signal.SIGINT, self.sigint_handler)
        
        self.run_server = True
        
        self.logger.info("Camera server starting up with ID {} (version {} {})".format(
            self.id, self.version_hash, time.ctime(int(self.version_time))))

    def run(self):

        self.run_server = True
        with self.camera_type() as self.camera:
            
            self.init_camera_defaults()
            while self.run_server:
                self.handle_request()

        self.control_connection.disconnect()
        self.led.set_colour(LedDriver.OFF)                    
        self.logger.info("Camera server ID {} shutdown".format(self.id))
        
    def sigint_handler(self, signum, frame):
    
        self.logger.info("Interrupt signal received, shutting down")
        self.run_server = False
            
    def init_camera_defaults(self):
        
        for param in self.camera_params:
            setattr(self.camera, param, self.camera_params[param][0])
            
    def set_client_connected(self, is_connected):
        
        self.client_connected = is_connected
        if is_connected:
            self.led.set_colour(LedDriver.GREEN)
        else:
            self.led.set_colour(LedDriver.YELLOW)
            
    def set_camera_param(self, param, val):
        
        param_set_ok = True
        
        if param in self.camera_params:
            try:
                setattr(self.camera, param, self.camera_params[param][1](val))
            except Exception as e:
                self.logger.error("Failed to set camera parameter {} : {}".format(param, e))
                param_set_ok = False
        else:
            self.logger.error("Attempt to set illegal camera parameter {}".format(param))
            param_set_ok = False
            
        return param_set_ok

    def do_capture(self, blink_led=False):

        capture_ok = True

        self.image_io.seek(0)
        self.image_io.truncate()

        try:
            self.camera.capture(self.image_io, format='jpeg', use_video_port=True)
            if (blink_led):
                self.led.blink(LedDriver.RED, LedDriver.GREEN, 0.1, 10)

        except self.camera_mod.PiCameraRuntimeError, e:
            capture_ok = False

        return capture_ok

    def get_image_size(self):

        return self.image_io.tell()

    def get_image_data(self):

        self.image_io.seek(0)

        return self.image_io.read()

class UDPHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        cur_thread = threading.current_thread()
        self.server.logger.debug("{} wrote: {}".format(self.client_address[0], data))

        self.server.command_parser.parse_command(data)


def get_version():

    vers_info = subprocess.check_output(['git', 'log', '-1', '--pretty=\'%h %ct\'']).strip().lstrip('\'').rstrip('\'').split()
    return vers_info

def parse_args():

    parser = argparse.ArgumentParser(description="Timeslice camera server")

    parser.add_argument('--version', action="store_true",
                        help="Display version information")
    parser.add_argument('--id', action="store", dest="id", type=int, default=0,
                        help="Camera ID, use IP address offset to resolve if specified")
    parser.add_argument('--idoffset', action="store", dest="idoffset", type=int, default=100,
                        help="Offset value used to resolve camera ID from IP address")
    parser.add_argument('--mcast_group', action="store", dest="mcast_group", default=MCAST_GRP,
                        help="Multicast group for camera server to bind to")
    parser.add_argument("--mcast_port", action="store", type=int, dest="mcast_port", default=MCAST_PORT,
                        help="Multicast port for camera server to bind to")
    parser.add_argument("--simulate", action="store_true", dest="simulate",
                        help="Use simulated camera bindings (debug feature)")
    parser.add_argument("--logging", action="store", default='info',
                        #metavar="debug|info|warning|error|none",
                        choices=['debug', 'info', 'warning', 'error', 'none'],
                        help="Set the logging level")

    args = parser.parse_args()

    if args.version:
        hash, commit_time = get_version()
        print "Commit {} at {}".format(hash, time.ctime(int(commit_time)))
        sys.exit(0)

    if args.id == 0:
        ipaddr = socket.gethostbyname(socket.gethostname())
        ipoct = int(ipaddr.split('.')[-1])
        args.id = ipoct - args.idoffset

    return args

def main():

    # Parse arguments
    args = parse_args()

    # Set up a custom logger
    logger.setup_logger('camera_server', args.logging)

    server = CameraServer(args)
    server.run()

if __name__ == '__main__':

    main()
