import os
import time

import tornado.gen
import tornado.web


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

class CameraWebServer(object):

    def __init__(self, control_mcast_client):

        settings = {
            "static_path": os.path.abspath(os.path.join(os.path.dirname(__file__), "../static")),
            }

        self.application = tornado.web.Application([
            (r"/", MainHandler),
            (r"/capture", CaptureHandler),
            (r"/connect", ConnectHandler),
        ], **settings)

        self.application.control_mcast_client = control_mcast_client

    def listen(self, port, host=''):

        self.application.listen(port, host)
