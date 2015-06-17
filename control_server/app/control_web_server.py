import os
import time
import json

import tornado.gen
import tornado.web
import tornado.ioloop

import logging

class MainHandler(tornado.web.RequestHandler):

    def get(self):
        self.redirect("/static/html/camera_control.html")

class CaptureHandler(tornado.web.RequestHandler):


    def post(self):
        self.application.camera_controller.do_capture()

class MonitorHandler(tornado.web.RequestHandler):

    def get(self):
        enabled = '1' if self.application.camera_controller.camera_monitor_enabled() == True else '0'
        #TODO this should return something in a useful format
        self.write(enabled)

    def post(self):
        enable = True if self.get_query_argument('enable', default='0') == '1' else False
        self.application.camera_controller.enable_camera_monitor(enable)
        logging.info("Setting camera state monitor enable to {}".format(enable))

class PreviewHandler(tornado.web.RequestHandler):

    def get(self):
        self.write("preview: {}".format(time.time()))

    def post(self):
        enable = True if self.get_query_argument('enable', default='0') == '1' else False
        camera = int(self.get_query_argument('camera', default='1'))
        update = int(self.get_query_argument('update', default='1'))

        logging.debug("Got preview POST request: enable={} camera={} update={}".format(enable, camera, update))

class CameraVersionHandler(tornado.web.RequestHandler):

    def post(self):
        self.application.camera_controller.control_mcast_client.send("version id=0")

    def get(self):
        version_info = self.application.camera_controller.get_camera_version_info()

        response = {}
        response['camera_version_commit'] = [elems[0] for elems in version_info]
        response['camera_version_time']   = [elems[1] for elems in version_info]

        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(response))

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
            (r"/preview", PreviewHandler),
            (r"/camera_version", CameraVersionHandler),
            (r"/camera_state", CameraStateHandler),
            (r"/camera_enable", CameraEnableHandler),
        ], **settings)


        self.application.camera_controller = camera_controller

    def listen(self, port, host=''):

        self.application.listen(port, host)
