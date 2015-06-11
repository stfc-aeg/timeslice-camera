import os
import time

import tornado.gen
import tornado.web
import tornado.ioloop

import logging

class MainHandler(tornado.web.RequestHandler):

    def get(self):
        #self.write("Hello, world!\n")
        self.redirect("/static/html/camera_control.html")

class CaptureHandler(tornado.web.RequestHandler):

    def get(self):
        self.application.control_mcast_client.send("capture test=1")
        time.sleep(2.0)
        self.write("Capture complete!")

class ConnectHandler(tornado.web.RequestHandler):

    def get(self):
        self.application.control_mcast_client.send("connect host=127.0.0.1 port=8008")
        time.sleep(2.0)
        self.write("Connect complete!")

class MonitorHandler(tornado.web.RequestHandler):

    def get(self):
        enabled = '1' if self.application.state_monitor_enable == True else '0'
        #TODO this should return something in a useful format
        self.write(enabled)

    def post(self):
        enabled = self.get_query_argument('enable', default=0)
        self.application.state_monitor_enable = True if enabled == '1' else False
        logging.info("Setting camera state monitor enable to {}".format(self.application.state_monitor_enable))

class CameraWebServer(object):

    def __init__(self, control_mcast_client):

        settings = {
            "static_path": os.path.abspath(os.path.join(os.path.dirname(__file__), "../static")),
            }

        self.application = tornado.web.Application([
            (r"/", MainHandler),
            (r"/capture", CaptureHandler),
            (r"/connect", ConnectHandler),
            (r"/monitor", MonitorHandler),
        ], **settings)


        self.application.control_mcast_client = control_mcast_client
        self.application.state_monitor_enable = False

        # Create a periodic callback that is used to track the camera state via ping commands
        self.state_monitor = tornado.ioloop.PeriodicCallback(self.state_monitor_callback, 1000)
        self.state_monitor.start()

#            lambda: self.state_monitor_callback(), 5)

    def listen(self, port, host=''):

        self.application.listen(port, host)

    def state_monitor_callback(self):

        if self.application.state_monitor_enable:
            logging.debug("State monitor running")
            self.application.control_mcast_client.send("ping id=0 host=127.0.0.1 port=8008")
