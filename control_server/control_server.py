import app.control_web_server
import app.control_mcast_client
import app.control_tcp_server
import app.camera_controller

import logging

import tornado.ioloop
import tornado.options
from tornado.options import options

def main():

    # Define configuration options and add to tornado option parser
    tornado.options.define("mcast_group", default="224.1.1.1", help="Set camera control multicast group address")
    tornado.options.define("mcast_port", default=5007, help="Set camera control multicast port")
    tornado.options.define("http_addr", default="0.0.0.0", help="Set HTTP server address")
    tornado.options.define("http_port", default=8888, help="Set HTTP server port")
    tornado.options.define("ctrl_addr", default="0.0.0.0", help="Set camera control server address")
    tornado.options.define("ctrl_port", default=8008, help="Set camera control server port")

    # Parse the command line options
    tornado.options.parse_command_line()

    # Create a multicast client for communication with cameras
    control_mcast_client = app.control_mcast_client.ControlMcastClient(options.mcast_group, options.mcast_port)

    logging.info("Camera control multicast client created on %s:%d..." % (options.mcast_group, options.mcast_port))

    # Launch the camera controller
    camera_controller = app.camera_controller.CameraController(control_mcast_client, options.ctrl_addr, options.ctrl_port)

    # Launch the HTTP server app for the control UI
    control_web_server = app.control_web_server.CameraWebServer(camera_controller)
    control_web_server.listen(options.http_port, options.http_addr)

    logging.info("Web server listening on %s:%d" % (options.http_addr, options.http_port))

    # Launch the control TCP server for receving data from the cameras
    control_tcp_server = app.control_tcp_server.ControlTcpServer(camera_controller)
    control_tcp_server.listen(options.ctrl_port, options.ctrl_addr)

    logging.info("Camera control server listening on %s:%d..." % (options.ctrl_addr, options.ctrl_port))

    # Enter IO processing loop
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
