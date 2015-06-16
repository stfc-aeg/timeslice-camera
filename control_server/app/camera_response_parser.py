import string
import logging

class CameraResponseParser(object):

    def __init__(self, camera_controller):

        self.camera_controller = camera_controller

        # Define dictionary of legal responses and assoicated methods
        self.responses = { 'PING_ACK'       : self.ping_response,
                        }

    def parse_response(self, response_data):

        response_ok = True

        # Split response into space separated list
        response_words = string.split(response_data)
        response = response_words[0].upper()

        # Test if first word, i.e. the response word, is a legal response
        if response in self.responses:

            # If so, split remaining words into key-value pairs separated by '=''
            try:
                args = dict(item.split("=") for item in response_words[1:])

                if 'id' in args:
                    try:
                        # Decode the id parameter 
                        id = int(args['id'])
                        response_ok = self.responses[response](id, args)

                    except ValueError:
                        response_ok = False
                        logging.error("Non-integer ID parameter specified on response: {}".format(args['id']))
                else:
                    response_ok = False
                    logging.error("No ID parameter present in command")

            except ValueError:
                response_ok = False
                logging.error("Illegal parameter format: {}".format(response_data))

        else:
            response_ok = False
            logging.error("Unrecognised response : {}".format(response))

        return response_ok

    def ping_response(self, id, args):

        logging.debug("Got ping response, ID={}, args={}".format(id, args))
        self.camera_controller.update_camera_last_ping_time(id)
