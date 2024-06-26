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

class RestartSystemHandler(tornado.web.RequestHandler):

    def post(self):
        self.application.camera_controller.reset_state_values()

class SaveVideoHandler(tornado.web.RequestHandler):

    def post(self):
        self.application.camera_controller.do_save()

class CaptureCountdownHandler(tornado.web.RequestHandler):

    def post(self):
        self.application.camera_controller.do_capture_countdown()

class CaptureTriggerHandler(tornado.web.RequestHandler):

    def post(self):
        self.application.camera_controller.do_capture(with_delay=True)

class CaptureConfigHandler(tornado.web.RequestHandler):

    def get(self):
        response = {}
        response['render_loop'] = self.application.camera_controller.get_render_loop()
        response['stagger_enable'] = '1' if self.application.camera_controller.get_stagger_enable() == True else '0'
        response['stagger_offset'] = self.application.camera_controller.get_stagger_offset()

        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(response))

    def post(self):

        render_loop = int(self.get_query_argument('render_loop', default='1'))
        stagger_enable = True if self.get_query_argument('stagger_enable', default='1') == '1' else False
        stagger_offset = int(self.get_query_argument('stagger_offset', default='0'))

        logging.debug("Got capture config POST request: render_loop={} stagger_enable={} stagger_offset={}".format(
            render_loop, stagger_enable, stagger_offset))
        self.application.camera_controller.set_capture_config(render_loop, stagger_enable, stagger_offset)

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
        self.set_header("Content-Type", "image/jpeg")
        self.set_header("Pragma", "no-cache")
        self.set_header("Expires", "Fri, 30 Oct 1998 14:19:41 GMT")
        self.set_header("Cache-Control", "no-cache, must-revalidate")
        self.write(self.application.camera_controller.get_preview_image())

class PreviewVideoHandler(tornado.web.RequestHandler):

    def get(self):
        self.set_header("Content-Type", "video/mp4")
        self.set_header("Pragma", "no-cache")
        self.set_header("Expires", "Fri, 30 Oct 1998 14:19:41 GMT")
        self.set_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.write(self.application.camera_controller.get_preview_video())

class PreviewConfigHandler(tornado.web.RequestHandler):

    def get(self):
        response = {}
        response['enable'] = '1' if self.application.camera_controller.get_preview_enable() == True else '0'
        response['camera'] = self.application.camera_controller.get_preview_camera()
        response['update'] = self.application.camera_controller.get_preview_update()

        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(response))

    def post(self):
        enable = True if self.get_query_argument('enable', default='0') == '1' else False
        camera = int(self.get_query_argument('camera', default='1'))
        update = int(self.get_query_argument('update', default='1'))

        logging.debug("Got preview POST request: enable={} camera={} update={}".format(enable, camera, update))
        self.application.camera_controller.set_preview_mode(enable, camera, update)

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
        response['access_code'] = self.application.camera_controller.get_access_code()
        response['camera_state'] = self.application.camera_controller.get_camera_state()
        response['camera_enable'] = self.application.camera_controller.get_camera_enable()
        response['system_state'] = self.application.camera_controller.get_system_state()
        response['system_status'] = self.application.camera_controller.get_system_status()
        response['capture_state'] = self.application.camera_controller.get_capture_state()
        response['capture_status'] = self.application.camera_controller.get_capture_status()
        response['configure_state'] = self.application.camera_controller.get_configure_state()
        response['configure_status'] = self.application.camera_controller.get_configure_status()
        response['last_render_file'] = self.application.camera_controller.get_last_render_file()
        response['process_status'] = self.application.camera_controller.get_process_status()
        response['retrieve_state'] = self.application.camera_controller.get_retrieve_state()
        response['render_state'] = self.application.camera_controller.get_render_state()
        response['capture_countdown_count'] = self.application.camera_controller.get_capture_countdown_count()

        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(response))

class CameraEnableHandler(tornado.web.RequestHandler):

    def post(self):
        logging.info("Got camera enable POST request of type {}".format(self.request.headers["Content-Type"]))
        json_args = json.loads(self.request.body)
        self.application.camera_controller.set_camera_enable(json_args['camera_enable'])

class CameraConfigHandler(tornado.web.RequestHandler):

    def post(self):
        logging.info("Got config POST request with query arguments {}".format(self.request.query_arguments))
        self.application.camera_controller.set_camera_params(self.request.query_arguments)

    def get(self):
        logging.info("Got config GET request with query arguments {}".format(self.request.query_arguments))
        response = self.application.camera_controller.get_camera_params(self.get_query_arguments('param'))
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(response))

class CameraCalibrateHandler(tornado.web.RequestHandler):

    def get(self):
        logging.info("Got calibrate GET request with query arguments {}".format(self.request.query_arguments))
        self.write("OK")

    def post(self):
        logging.info("Got calibrate POST request with query arguments {}".format(self.request.query_arguments))
        camera = int(self.get_query_argument('camera', default='1'))
        self.application.camera_controller.do_calibrate(camera)

        self.write("OK")

class CameraWebServer(object):

    def __init__(self, camera_controller):

        settings = {
            "static_path": os.path.abspath(os.path.join(os.path.dirname(__file__), "../static")),
            }

        self.application = tornado.web.Application([
            (r"/", MainHandler),
            (r"/capture", CaptureHandler),
            (r"/capture_trigger", CaptureTriggerHandler),
            (r"/capture_countdown", CaptureCountdownHandler),
            (r"/capture_config", CaptureConfigHandler),
            (r"/monitor", MonitorHandler),
            (r"/preview", PreviewHandler),
            (r"/preview_config", PreviewConfigHandler),
            (r"/camera_version", CameraVersionHandler),
            (r"/camera_state", CameraStateHandler),
            (r"/camera_enable", CameraEnableHandler),
            (r"/camera_config", CameraConfigHandler),
            (r"/calibrate", CameraCalibrateHandler),
            (r"/reset_states", RestartSystemHandler),
            (r"/save_video", SaveVideoHandler),
            (r"/preview_video", PreviewVideoHandler),
        ], **settings)


        self.application.camera_controller = camera_controller

    def listen(self, port, host=''):

        self.application.listen(port, host)
