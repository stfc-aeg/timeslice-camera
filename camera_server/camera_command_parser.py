import string
import logger

class CameraCommandParser(object):

    def __init__(self, server):

        # Define dictionary of legal commands and assoicated methods
        self.commands = { 'CONNECT'    : self.connect_cmd,
                          'DISCONNECT' : self.disconnect_cmd,
                          'PING'       : self.ping_cmd,
                          'CAPTURE'    : self.capture_cmd,
                          'SET'        : self.set_cmd,
                          'GET'        : self.get_cmd,
                        }

        self.server = server

        self.logger = logger.get_logger()

    def parse_command(self, cmd_data):
        """
        Command parser - takes a line of space-separated data and parses it
        into a command and associated parameter arguments
        """

        cmd_ok = True

        # Split data into space separated list
        cmd_words = string.split(cmd_data)

        #print ">>>", cmd_words

        command = cmd_words[0].upper()

        # Test if first word, i.e. the command word, is a legal command
        if command in self.commands:

            # If so, split remaining words into key-value pairs separated by '=''
            try:
                args = dict(item.split("=") for item in cmd_words[1:])

                if 'id' in args:

                    try:
                        id = int(args['id'])
                        print id
                        if id == 0 or id == self.server.id:

                            # Pass arguments to command method
                            cmd_ok = self.commands[command](args)

                    except ValueError:
                        cmd_ok = False
                        self.logger.error("Non-integer ID parameter specified on command: {}".format(args['id']))


                else:
                    cmd_ok = False
                    self.logger.error("No ID parameter present in command")

            except ValueError:
                cmd_ok = False
                self.logger.error("Illegal parameter format: {}".format(cmd_data))

        else:
            cmd_ok = False
            self.logger.error("Unrecognised command : {}".format(command))

        # Format response depending on success of command
        if not cmd_ok:
            self.logger.error("Command failed")

        return cmd_ok

    def connect_cmd(self, args):
        self.logger.debug("Connect command")
        return True

    def disconnect_cmd(self, args):
        self.logger.debug("Disconnect command")
        return True

    def ping_cmd(self, args):
        self.logger.debug("Ping command, args={}".format(args))
        return True

    def capture_cmd(self, args):
        self.logger.debug("Capture command")
        return True

    def set_cmd(self, args):
        self.logger.debug("Set command")
        return True

    def get_cmd(self, args):
        self.logger.debug("Get command")
        return True
