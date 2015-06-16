import tornado.ioloop
import logging
import camera_response_parser
import time

class CameraController(object):

    MAX_CAMERAS = 48

    SYSTEM_STATE_NOT_READY = 0
    SYSTEM_STATE_READY     = 1
    SYSTEM_STATE_CAPTURING = 2

    CAMERA_STATE_DEAD  = 0
    CAMERA_STATE_ALIVE = 1


    def __init__(self, control_mcast_client):

        self.control_mcast_client = control_mcast_client

        self.response_parser = camera_response_parser.CameraResponseParser(self)

        self.system_state = CameraController.SYSTEM_STATE_NOT_READY
        self.system_status = "Not ready"

        self.camera_state = [CameraController.CAMERA_STATE_DEAD]  * (CameraController.MAX_CAMERAS+1)
        self.camera_last_ping_time = [0.0] * (CameraController.MAX_CAMERAS+1)
        self.camera_enabled = [0] * (CameraController.MAX_CAMERAS+1)
        self.camera_enabled[1] = 1
        self.camera_enabled[2] = 1

        self.camera_monitor_enable = True
        self.camera_monitor_loop_ratio = 10
        self.camera_monitor_loop = self.camera_monitor_loop_ratio

        self.camera_max_ping_age = 2.0

        self.controller_period = 100
        self.controller = tornado.ioloop.PeriodicCallback(self.controller_callback, self.controller_period)
        self.controller.start()

        logging.info("State controller started")

    def controller_callback(self):

        if self.camera_monitor_enable:
            self.camera_monitor_loop -= 1
            if self.camera_monitor_loop == 0:

                logging.debug("Camera monitor fired")
                self.control_mcast_client.send("ping id=0 host=127.0.0.1 port=8008")

                now = time.time()
                for camera in range(1, CameraController.MAX_CAMERAS+1):
                    if (now - self.camera_last_ping_time[camera]) < self.camera_max_ping_age:
                        self.camera_state[camera] = CameraController.CAMERA_STATE_ALIVE
                    else:
                        self.camera_state[camera] = CameraController.CAMERA_STATE_DEAD

                num_enabled_cameras = sum(self.camera_enabled)
                num_enabled_cameras_alive = sum([(enabled and (state == CameraController.CAMERA_STATE_ALIVE))
                    for (enabled, state) in zip(self.camera_enabled[1:], self.camera_state[1:])])
                if num_enabled_cameras == num_enabled_cameras_alive:
                    self.system_state = CameraController.SYSTEM_STATE_READY
                    status_flag = ""
                else:
                    self.system_state = CameraController.SYSTEM_STATE_NOT_READY
                    status_flag = "NOT "
                self.system_status = "System {}ready, {}/{} cameras alive".format(
                    status_flag, num_enabled_cameras_alive, num_enabled_cameras)

                self.camera_monitor_loop = self.camera_monitor_loop_ratio

    def enable_camera_monitor(self, enable):

        self.camera_monitor_enable = enable

    def camera_monitor_enabled(self):

        return self.camera_monitor_enable

    def get_camera_state(self):

        return self.camera_state[1:]

    def get_camera_enable(self):

        return self.camera_enabled[1:]

    def set_camera_enable(self, camera_enable):

        logging.debug(camera_enable)
        self.camera_enabled = [0] + camera_enable

    def get_system_state(self):

        return self.system_state

    def get_system_status(self):

        return self.system_status

    def do_capture(self):

        self.control_mcast_client.send("capture id=0 test=1")


    def process_camera_response(self, response):

        response_ok = self.response_parser.parse_response(response)

    def update_camera_last_ping_time(self, id):

        if id < 1 or id > CameraController.MAX_CAMERAS:
            logging.warning("Got camera ping response for illegal ID: {}".format(id))
        else:
            self.camera_last_ping_time[id] = time.time()
