import socket
import os
import logging

import tornado.gen
import tornado.iostream
import tornado.tcpserver

class CameraTcpConnection(object):
    client_id = 0

    def __init__(self, stream):
        #super().__init__()
        CameraTcpConnection.client_id += 1
        self.id = CameraTcpConnection.client_id
        self.stream = stream

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
        try:
            while True:
                line = yield self.stream.read_until(b'\n')
                self.log('got |%s|' % line.decode('utf-8').strip())
                #yield self.stream.write(line)
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

    @tornado.gen.coroutine
    def handle_stream(self, stream, address):
        """
        Called for each new connection, stream.socket is
        a reference to socket object
        """
        connection = CameraTcpConnection(stream)
        yield connection.on_connect()
