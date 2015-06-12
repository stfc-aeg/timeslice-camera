import socket
import struct
import logging

class ControlMcastClient(object):

    def __init__(self, mcast_group='224.1.1.1', mcast_port=5007):

      self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
      self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)

      self.mcast_group = mcast_group
      self.mcast_port  = mcast_port


    def send(self, data):

        try:
            self.socket.sendto(data, (self.mcast_group, self.mcast_port))
        except socket.error,e:
            logging.error("Error sending on message on mcast socket: {}".format(e))
