import tornado.ioloop
import logging
import time
import subprocess
import shlex
import os

import camera_response_parser

class CameraController(object):

    MAX_CAMERAS = 48

    SYSTEM_STATE_NOT_READY = 0
    SYSTEM_STATE_READY     = 1

    CAMERA_STATE_DEAD  = 0
    CAMERA_STATE_ALIVE = 1

    CAPTURE_STATE_IDLE        = 0
    CAPTURE_STATE_CAPTURING   = 1
    CAPTURE_STATE_CAPTURED    = 2
    CAPTURE_STATE_RETRIEVING  = 3
    CAPTURE_STATE_RETRIEVED   = 4
    CAPTURE_STATE_RENDERING   = 5

    def __init__(self, control_mcast_client, control_addr, control_port):

        self.control_mcast_client = control_mcast_client
        self.control_addr = control_addr
        self.control_port = control_port
        
        self.response_parser = camera_response_parser.CameraResponseParser(self)

        self.system_state = CameraController.SYSTEM_STATE_NOT_READY
        self.system_status = "Not ready"

        self.camera_state = [CameraController.CAMERA_STATE_DEAD]  * (CameraController.MAX_CAMERAS+1)
        self.camera_last_ping_time = [0.0] * (CameraController.MAX_CAMERAS+1)
        self.camera_version_info   = [('Unknown', '0')] * (CameraController.MAX_CAMERAS+1)
        self.camera_enabled = [0] * (CameraController.MAX_CAMERAS+1)
        self.camera_enabled[1] = 1
        self.camera_enabled[2] = 1

        self.camera_capture_state = [CameraController.CAPTURE_STATE_IDLE] * (CameraController.MAX_CAMERAS+1)
        self.capture_state = CameraController.CAPTURE_STATE_IDLE
        self.capture_status = "Idle"

        self.capture_time = 0.0
        self.retrieve_time = 0.0
        self.render_time = 0.0

        self.render_process = None
        self.camera_monitor_enable = True
        self.camera_monitor_loop_ratio = 10
        self.camera_monitor_loop = self.camera_monitor_loop_ratio

        self.preview_enable = False
        self.preview_camera = 0
        self.preview_update = 0
        self.preview_time = 0.0

        self.preview_id = 0
        self.preview_image = ''

        default_preview_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "../static/img/testcard.jpg"))
        with open(default_preview_file, 'rb') as preview_file:
            self.preview_image = preview_file.read()

        self.camera_max_ping_age = 4.0
        self.capture_timeout = 5.0
        self.retrieve_timeout = 5.0
        self.render_timeout = 5.0

        self.controller_period = 100
        self.controller = tornado.ioloop.PeriodicCallback(self.controller_callback, self.controller_period)
        self.controller.start()

        logging.info("State controller started")

    def controller_callback(self):

        self.handle_capture_state()
        self.handle_preview_update()
        self.monitor_camera_state()

    def handle_capture_state(self):

        # Validate the current capture state and check if any pending captures are running

        if self.capture_state == CameraController.CAPTURE_STATE_IDLE:
            # Do nothing
            pass

        elif self.capture_state == CameraController.CAPTURE_STATE_CAPTURING:
            # num_cameras_capturing = sum([(enabled and (state == CameraController.CAPTURE_STATE_CAPTURING))
            #     for (enabled, state) in zip(self.camera_enabled[1:], self.camera_capture_state[1:])])
            num_cameras_capturing = self.get_num_enabled_in_state(CameraController.CAPTURE_STATE_CAPTURING, self.camera_capture_state)
            capture_elapsed_time = time.time() - self.capture_time
            if num_cameras_capturing > 0:
                if capture_elapsed_time > self.capture_timeout:
                    self.capture_status = "Captured timed out on {} cameras".format(num_cameras_capturing)
                    logging.error(self.capture_status)
                    self.capture_state = CameraController.CAPTURE_STATE_IDLE
            else:
                self.capture_status = "Camera capture completed OK after {:.3f} secs".format(capture_elapsed_time)
                logging.info(self.capture_status)
                self.do_retrieve()

        elif self.capture_state == CameraController.CAPTURE_STATE_RETRIEVING:

            num_cameras_retrieving = self.get_num_enabled_in_state(CameraController.CAPTURE_STATE_RETRIEVING, self.camera_capture_state)
            retrieve_elapsed_time = time.time() - self.retrieve_time
            if num_cameras_retrieving > 0:
                if retrieve_elapsed_time > self.retrieve_timeout:
                    self.capture_status = "Retrieve timed out on {} cameras".format(num_cameras_retrieving)
                    logging.error(self.capture_status)
                    self.capture_state = CameraController.CAPTURE_STATE_IDLE
            else:
                self.capture_status = "Image retrieve completed OK after {:.3f} secs".format(retrieve_elapsed_time)
                logging.info(self.capture_status)
                self.do_render()

        elif self.capture_state == CameraController.CAPTURE_STATE_RENDERING:

            render_state = self.render_process.poll()
            render_elapsed_time = time.time() - self.retrieve_time

            if render_state is None:
                if render_elapsed_time > self.render_timeout:
                    self.capture_status = "Timeslice render timed out"
                    self.capture_state = CameraController.CAPTURE_STATE_IDLE
            else:
                (render_stdout, render_stderr) = self.render_process.communicate()
                if render_state == 0:
                    self.capture_status = "Timeslice render completed OK after {:.3f} secs".format(render_elapsed_time)
                    logging.info(self.capture_status)
                else:
                    self.capture_state = "Timeslice render failed with return code {}".format(render_state)
                    logging.error(self.capture_status)
                    logging.error("Render output:\n{}\n{}".format(render_stdout, render_stderr))

                self.capture_state = CameraController.CAPTURE_STATE_IDLE

    def handle_preview_update(self):

        if self.preview_enable:

            if (time.time() - self.preview_time) > self.preview_update:
                logging.debug("Preview update fired")

                self.control_mcast_client.send("preview id={}".format(self.preview_camera))
                self.preview_time = time.time()

    def monitor_camera_state(self):

        # Run the camera periodic monitoring if enabled
        if self.camera_monitor_enable:
            self.camera_monitor_loop -= 1
            if self.camera_monitor_loop == 0:

                logging.debug("Camera monitor fired")
                self.control_mcast_client.send("ping id=0 host={} port={}".format(self.control_addr, self.control_port))

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
                    status_flag = "Ready"
                else:
                    self.system_state = CameraController.SYSTEM_STATE_NOT_READY
                    status_flag = "NOT ready"
                self.system_status = "{}, {}/{} cameras alive".format(
                    status_flag, num_enabled_cameras_alive, num_enabled_cameras)

                self.camera_monitor_loop = self.camera_monitor_loop_ratio

    def get_num_enabled_in_state(self, desired_state, object_state):

        return sum([(enabled and (state == desired_state))
            for (enabled, state) in zip(self.camera_enabled[1:], object_state[1:])])

    def enable_camera_monitor(self, enable):

        self.camera_monitor_enable = enable

    def camera_monitor_enabled(self):

        return self.camera_monitor_enable

    def get_camera_state(self):

        return self.camera_state[1:]

    def get_camera_enable(self):

        return self.camera_enabled[1:]

    def set_camera_enable(self, camera_enable):

        self.camera_enabled = [0] + camera_enable

    def get_system_state(self):

        return self.system_state

    def get_system_status(self):

        return self.system_status

    def get_capture_state(self):

        return self.capture_state

    def get_capture_status(self):

        return self.capture_status

    def get_camera_version_info(self):

        return self.camera_version_info[1:]

    def get_preview_image(self):

        return self.preview_image

    def set_preview_mode(self, enable, camera, update):

        self.preview_enable = enable
        self.preview_camera = camera
        self.preview_update = update

    def do_capture(self):

        # Set the capture state to capturing, set the capture time
        self.capture_state = CameraController.CAPTURE_STATE_CAPTURING
        self.capture_time = time.time()
        self.capture_status = "Capture in progress"

        # Set state of enabled cameras to capturing
        for camera in range(1, CameraController.MAX_CAMERAS+1):
            if self.camera_enabled[camera]:
                self.camera_capture_state[camera] = CameraController.CAPTURE_STATE_CAPTURING

        self.control_mcast_client.send("capture id=0 test=1")

    def do_retrieve(self):

        # Set the capture state to retrieving, set the capture time
        self.capture_state = CameraController.CAPTURE_STATE_RETRIEVING
        self.retrieve_time = time.time()
        self.capture_status = "Image retrieve in progress"

        # Set state of enabled cameras to retrieving
        for camera in range(1, CameraController.MAX_CAMERAS+1):
            if self.camera_enabled[camera]:
                self.camera_capture_state[camera] = CameraController.CAPTURE_STATE_RETRIEVING

        self.control_mcast_client.send("retrieve id=0")

    def do_render(self):

        self.capture_state = CameraController.CAPTURE_STATE_RENDERING
        self.render_time = time.time()
        self.capture_status = "Timeslice render in progress"

        render_cmd = "ffmpeg -framerate 2 -i \'/tmp/image_%02d.jpg\' -codec copy -y /tmp/timeslice.mkv"
        logging.info("Launching render process with command: {}".format(render_cmd))

        self.render_process = subprocess.Popen(shlex.split(render_cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)


    def process_camera_response(self, response):

        response_ok = self.response_parser.parse_response(response)

    def update_camera_last_ping_time(self, id):

        if id < 1 or id > CameraController.MAX_CAMERAS:
            logging.warning("Got camera ping response for illegal ID: {}".format(id))
        else:
            self.camera_last_ping_time[id] = time.time()

    def update_camera_version_info(self, id, commit, time):

        if id < 1 or id > CameraController.MAX_CAMERAS:
            logging.warning("Got version response for illegal ID: {}".format(id))
        else:
            self.camera_version_info[id] = (commit, time)


    def update_camera_capture_state(self, id, did_ack):

        if id < 1 or id > CameraController.MAX_CAMERAS:
            logging.warning("Got camera capture response for illegal ID: {}".format(id))
        else:
            if self.camera_capture_state[id] != CameraController.CAPTURE_STATE_CAPTURING:
                logging.warning("Got capture response for camera ID {} when not in capturing state".format(id))
            elif not did_ack:
                logging.warning("Camera ID {} responded with no-acknowledge for capture command".format(id))

            self.camera_capture_state[id] = CameraController.CAPTURE_STATE_CAPTURED

    def update_camera_retrieve_state(self, id, did_ack, image_data):

        if id < 0 or id > CameraController.MAX_CAMERAS:
            logging.warning("Got camera retrieve response for illegal ID: {}".format(id))
        else:
            if self.camera_capture_state[id] != CameraController.CAPTURE_STATE_RETRIEVING:
                logging.warning("Got retrieve response for camera ID {} when not in retrieving state".format(id))
            elif not did_ack:
                logging.warning("Camera ID {} responded with no-acknowledge for retrieve command".format(id))

            self.camera_capture_state[id] = CameraController.CAPTURE_STATE_RETRIEVED

            if image_data is not None and len(image_data) > 0:
                image_file_name = "/tmp/image_{:02d}.jpg".format(id)
                image_file = open(image_file_name, 'wb')
                image_file.write(image_data)
                image_file.close()
                logging.info("Wrote image data for camera {} to file {}".format(id, image_file_name))

    def update_preview_image(self, id, image_data):

        self.preview_image_id = id
        self.preview_image = image_data
