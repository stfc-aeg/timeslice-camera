import socket
import os
import logging
import struct

import tornado.gen
import tornado.iostream
import tornado.tcpserver

class CameraTcpConnection(object):
    client_id = 0

    def __init__(self, stream, camera_controller):

        self.stream = stream
        self.camera_controller = camera_controller

        CameraTcpConnection.client_id += 1
        self.id = CameraTcpConnection.client_id

        self.stream.socket.setsockopt(
            socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.stream.socket.setsockopt(
            socket.IPPROTO_TCP, socket.SO_KEEPALIVE, 1)
        self.stream.set_close_callback(self.on_disconnect)


    @tornado.gen.coroutine
    def on_disconnect(self):
        self.log("disconnected")
        yield []

    @tornado.gen.coroutine
    def dispatch_client(self):
        
        hdr_fmt = '<L'
        hdr_size = struct.calcsize(hdr_fmt)
        data_size = 0
        
        try:
            while True:
                # Read the message size header first
                hdr = yield self.stream.read_bytes(hdr_size)
                data_size = struct.unpack(hdr_fmt, hdr)[0]

                # Read the message itself                    
                response = yield self.stream.read_bytes(data_size)

                self.log('got response with length %d bytes' % len(response))
                self.camera_controller.process_camera_response(response)

        except tornado.iostream.StreamClosedError:
            pass

    @tornado.gen.coroutine
    def on_connect(self):
        raddr = 'closed'
        try:
            raddr = '%s:%d' % self.stream.socket.getpeername()
        except Exception:
            pass
        self.log('new, %s' % raddr)

        yield self.dispatch_client()

    def log(self, msg, *args, **kwargs):
        logging.debug('[connection %d] %s' % (self.id, msg.format(*args, **kwargs)))


class ControlTcpServer(tornado.tcpserver.TCPServer):

    def __init__(self, camera_controller, *args, **kwargs):

        self.camera_controller = camera_controller
        super(ControlTcpServer, self).__init__(*args, **kwargs)

    @tornado.gen.coroutine
    def handle_stream(self, stream, address):
        """
        Called for each new connection, stream.socket is
        a reference to socket object
        """
        connection = CameraTcpConnection(stream, self.camera_controller)
        yield connection.on_connect()
