import os
import time
import json

import tornado.gen
import tornado.web
import tornado.ioloop

import logging

class MainHandler(tornado.web.RequestHandler):

    def get(self):
        #self.write("Hello, world!\n")
        self.redirect("/static/html/camera_control.html")

class CaptureHandler(tornado.web.RequestHandler):


    def post(self):
        #self.application.control_mcast_client.send("capture test=1")
        self.application.camera_controller.do_capture()
        #time.sleep(2.0)
        #self.write("Capture complete!")

class MonitorHandler(tornado.web.RequestHandler):

    def get(self):
        enabled = '1' if self.application.camera_controller.camera_monitor_enabled() == True else '0'
        #TODO this should return something in a useful format
        self.write(enabled)

    def post(self):
        enable = True if self.get_query_argument('enable', default='0') == '1' else False
        self.application.camera_controller.enable_camera_monitor(enable)
        logging.info("Setting camera state monitor enable to {}".format(enable))

class CameraStateHandler(tornado.web.RequestHandler):

    def get(self):
        response = {}
        response['camera_state'] = self.application.camera_controller.get_camera_state()
        response['camera_enable'] = self.application.camera_controller.get_camera_enable()
        response['system_state'] = self.application.camera_controller.get_system_state()
        response['system_status'] = self.application.camera_controller.get_system_status()
        response['capture_state'] = self.application.camera_controller.get_capture_state()
        response['capture_status'] = self.application.camera_controller.get_capture_status()

        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(response))

class CameraEnableHandler(tornado.web.RequestHandler):

    def post(self):
        logging.info("Got camera enable POST request of type {}".format(self.request.headers["Content-Type"]))
        json_args = json.loads(self.request.body)
        logging.info(self.request.body)
        self.application.camera_controller.set_camera_enable(json_args['camera_enable'])

class CameraWebServer(object):

    def __init__(self, camera_controller):

        settings = {
            "static_path": os.path.abspath(os.path.join(os.path.dirname(__file__), "../static")),
            }

        self.application = tornado.web.Application([
            (r"/", MainHandler),
            (r"/capture", CaptureHandler),
            (r"/monitor", MonitorHandler),
            (r"/camera_state", CameraStateHandler),
            (r"/camera_enable", CameraEnableHandler),
        ], **settings)


        self.application.camera_controller = camera_controller

    def listen(self, port, host=''):

        self.application.listen(port, host)
