import os
import time

import tornado.gen
import tornado.web


class MainHandler(tornado.web.RequestHandler):

    def get(self):
        #self.write("Hello, world!\n")
        self.redirect("/static/html/index.html")

class CaptureHandler(tornado.web.RequestHandler):

    def get(self):
        self.application.control_mcast_client.send("Capture!!!")
        time.sleep(2.0)
        self.write("Woo-hoo!!")

class CameraWebServer(object):

    def __init__(self, control_mcast_client):

        settings = {
            "static_path": os.path.abspath(os.path.join(os.path.dirname(__file__), "../static")),
            }

        self.application = tornado.web.Application([
            (r"/", MainHandler),
            (r"/capture", CaptureHandler),
        ], **settings)

        self.application.control_mcast_client = control_mcast_client

    def listen(self, port, host=''):

        self.application.listen(port, host)
