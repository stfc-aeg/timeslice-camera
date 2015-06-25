import string
import logger

class hasRequiredParams(object):

    def __init__(self, required_params):

        self.required_params = required_params

    def __call__(self, func):

        def wrapped_func(*args):
            cmd_ok = True
            for param in self.required_params:
                if param not in args[1]:
                    cmd_ok = False
                    logger.get_logger().error("{} missing required parameter: {}".format(func.__name__, param))
            if cmd_ok:
                cmd_ok = func(*args)
            return cmd_ok
        return wrapped_func

class CameraCommandParser(object):

    def __init__(self, server):

        # Define dictionary of legal commands and assoicated methods
        self.commands = {
                          'PING'       : self.ping_cmd,
                          'VERSION'    : self.version_cmd,
                          'PREVIEW'    : self.preview_cmd,
                          'CAPTURE'    : self.capture_cmd,
                          'RETRIEVE'   : self.retrieve_cmd,
                          'CONFIGURE'  : self.configure_cmd,
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
                        # Decode the id parameter and only run the command if it is intended for
                        # this camera node or for all (id=0)
                        id = int(args['id'])

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

    @hasRequiredParams(['host', 'port'])
    def ping_cmd(self, args):

        cmd_ok = True
        self.logger.debug("Ping command, args={}".format(args))

        host = args['host']
        port = int(args['port'])
        if not self.server.control_connection.is_connected():
            self.server.control_connection.connect(host, port)

        self.server.control_connection.send('ping_ack id={}\n'.format(self.server.id))

        return cmd_ok

    def version_cmd(self, args):

        cmd_ok = True
        self.logger.debug("Version command")

        self.server.control_connection.send('version_ack id={} commit={} time={}'.format(
            self.server.id, self.server.version_hash, self.server.version_time))

        return cmd_ok

    def preview_cmd(self, args):

        preview_ok = True
        self.logger.debug("Preview command")

        preview_ok = self.server.do_capture(False, False, 0)

        image_size = 0

        if preview_ok:
            image_size = self.server.get_image_size()
            if image_size <= 0:
                preview_ok = False
                self.logger.error("Preview command failed, returned image data size = {}".format(image_size))

        if preview_ok:
            response_cmd = 'preview_ack'
        else:
            response_cmd = 'preview_nack'

        response = '{} id={} size={} raw_data='.format(response_cmd, self.server.id, image_size)
        response = response + self.server.get_image_data()
        self.server.control_connection.send(response)

        return preview_ok

    def capture_cmd(self, args):

        self.logger.debug("Capture command")

        stagger_enable = False
        stagger_offset = 0
        
        print args
        if 'stagger_enable' in args:
            stagger_enable = True if args['stagger_enable'] == '1' else False
        if 'stagger_offset' in args:
            try:
                stagger_offset = int(args['stagger_offset'])
            except ValueError, e:
                self.logging.error("Illegal stagger_offset argument received: {}".format(e))
             
        capture_ok = self.server.do_capture(True, stagger_enable, stagger_offset)

        if capture_ok:
            response_cmd = 'capture_ack'
        else:
            response_cmd = 'capture_nack'

        self.server.control_connection.send('{} id={}\n'.format(response_cmd, self.server.id))

        return capture_ok

    def retrieve_cmd(self, args):
        self.logger.debug("Retrieve command")

        retrieve_ok = True

        image_size = self.server.get_image_size()

        if image_size <= 0:
            retrieve_ok = False

        if retrieve_ok:
            response_cmd = 'retrieve_ack'
        else:
            response_cmd = 'retrieve_nack'

        response = '{} id={} size={} raw_data='.format(response_cmd, self.server.id, image_size)
        response = response + self.server.get_image_data()
        self.server.control_connection.send(response)

        return retrieve_ok

    def configure_cmd(self, args):
        self.logger.debug("Configure command")

        set_ok = True
        self.logger.debug("Configure command: {}".format(args))
        for param, val in args.iteritems():
            if param != 'id':
                param_ok = self.server.set_camera_param(param, val)
                if not param_ok:
                    set_ok = False

        if set_ok:
            response_cmd = "configure_ack"
        else:
            response_cmd = "configure_nack"

        self.server.control_connection.send('{} id={}\n'.format(response_cmd, self.server.id))

        return set_ok

    def get_cmd(self, args):
        self.logger.debug("Get command")
        return True
