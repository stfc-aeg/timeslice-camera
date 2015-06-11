import app.control_web_server
import app.control_mcast_client
import app.control_tcp_server
import logging

import tornado.ioloop
import tornado.options

def main():

    tornado.options.parse_command_line()

    # Create a custom logger
    #logger = app.logger.setup_logger('control_server')

    # Craete a multicast client for communication with cameras
    mcast_group = '224.1.1.1'
    mcast_port  = 5007
    control_mcast_client = app.control_mcast_client.ControlMcastClient(mcast_group, mcast_port)

    logging.info("Camera control multicat client created on %s:%d..." % (mcast_group, mcast_port))

    # Launch the Web server app for the control UI
    web_host = '0.0.0.0'
    web_port = 8888
    control_web_server = app.control_web_server.CameraWebServer(control_mcast_client)
    control_web_server.listen(web_port, web_host)

    logging.info("Web server listening on %s:%d" % (web_host, web_port))

    # Launch the control TCP server for receving data from the cameras
    tcp_host = '0.0.0.0'
    tcp_port = 8008
    control_ = app.control_tcp_server.ControlTcpServer()
    control_.listen(tcp_port, tcp_host)

    logging.info("Camera control server listening on %s:%d..." % (tcp_host, tcp_port))

    # Enter IO processing loop
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
