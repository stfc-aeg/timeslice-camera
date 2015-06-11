import string

class CameraCommandParser(object):

    def __init__(self, camera):

        # Define dictionary of legal commands and assoicated methods
        self.commands = { 'CONNECT'    : self.connect_cmd,
                          'DISCONNECT' : self.disconnect_cmd,
                          'PING'       : self.ping_cmd,
                          'CAPTURE'    : self.capture_cmd,
                          'SET'        : self.set_cmd,
                          'GET'        : self.get_cmd,
                        }

        self.camera = camera

    def parse_command(self, cmd_data):
        """
        Command parser - takes a line of space-separated data and parses it
        into a command and associated parameter arguments
        """

        # Split data into space separated list
        cmd_words = string.split(cmd_data)

        #print ">>>", cmd_words

        command = cmd_words[0].upper()

        # Test if first word, i.e. the command word, is a legal command
        if command in self.commands:

            # If so, split remaining words into key-value pairs separated by '=''
            try:
                args = dict(item.split("=") for item in cmd_words[1:])

                # Pass arguments to command method
                cmd_ok = self.commands[command](args)

            except ValueError:
                cmd_ok = False
                print("Illegal parameter format: {}".format(cmd_data))

        else:
            cmd_ok = False
            print("Unrecognised command : {}".format(command))

        # Format response depending on success of command
        if not cmd_ok:
            print("Command failed")

        return cmd_ok

    def connect_cmd(self, args):
        print("Connect command")
        return True

    def disconnect_cmd(self, args):
        print("Disconnect command")
        return True

    def ping_cmd(self, args):
        print("Ping command")
        return True

    def capture_cmd(self, args):
        print("Capture command")
        return True

    def set_cmd(self, args):
        print("Set command")
        return True

    def get_cmd(self, args):
        print("Get command")
        return True
