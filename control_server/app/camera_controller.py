import tornado.ioloop
import logging
import time
import subprocess
import shlex
import os
import glob
import shutil
import string
import random

import camera_response_parser

class CameraController(object):

    MAX_CAMERAS = 48

    SYSTEM_STATE_NOT_READY = 0
    SYSTEM_STATE_READY     = 1

    CAMERA_STATE_DEAD  = 0
    CAMERA_STATE_ALIVE = 1

    CONFIGURE_STATE_NOT_READY   = 0
    CONFIGURE_STATE_CONFIGURING = 1
    CONFIGURE_STATE_READY       = 2

    CAPTURE_STATE_IDLE                  = 0
    CAPTURE_STATE_CAPTURING             = 1
    CAPTURE_STATE_CAPTURING_FAILED      = 2
    CAPTURE_STATE_CAPTURING_COMPLETED   = 3

    RETRIEVE_STATE_IDLE                 = 0
    RETRIEVE_STATE_RETRIEVING           = 1
    RETRIEVE_STATE_RETRIEVING_FAILED    = 2
    RETRIEVE_STATE_RETRIEVING_COMPLETED = 3

    RENDER_STATE_IDLE                  = 0
    RENDER_STATE_RENDERING             = 1
    RENDER_STATE_RENDERING_FAILED      = 2
    RENDER_STATE_RENDERING_COMPLETED   = 3    

    RENDER_STATUS_IDLE = 0
    RENDER_STATUS_RENDERING = 1
    RENDER_STATUS_RENDERING_FAILED = 2
    RENDER_STATUS_RENDERING_COMPLETED = 3

    def __init__(self, control_mcast_client, control_addr, control_port, output_path):

        self.control_mcast_client = control_mcast_client
        self.control_addr = control_addr
        self.control_port = control_port
        self.output_path = output_path

        self.response_parser = camera_response_parser.CameraResponseParser(self)

        self.system_state = CameraController.SYSTEM_STATE_NOT_READY
        self.system_status = "Not ready"

        self.camera_state = [CameraController.CAMERA_STATE_DEAD]  * (CameraController.MAX_CAMERAS+1)
        self.camera_last_ping_time = [0.0] * (CameraController.MAX_CAMERAS+1)
        self.camera_version_info   = [('Unknown', '0')] * (CameraController.MAX_CAMERAS+1)
        self.camera_enabled = [0] * (CameraController.MAX_CAMERAS+1)

        for cam in range(1, CameraController.MAX_CAMERAS+1):
            self.camera_enabled[cam] = 1

        self.camera_params = {
            'resolution'    : '1024x768',
            'framerate'     : '30',
            'shutter_speed' : '300000',
            'iso'           : '100',
            'exposure_mode' : 'fixedfps',
            'color_effects' : 'None',
            'contrast'      : '0',
            'drc_strength'  : 'off',
            'awb_mode'      : 'off',
            'awb_gains'     : '1.5,1.5',
            'brightness'    : '50'
        }

        self.camera_configure_state = [CameraController.CONFIGURE_STATE_NOT_READY] * (CameraController.MAX_CAMERAS+1)
        self.configure_state = CameraController.CONFIGURE_STATE_NOT_READY
        self.configure_status = "Not ready"

        self.camera_capture_state = [CameraController.CAPTURE_STATE_IDLE] * (CameraController.MAX_CAMERAS+1)
        self.capture_state = CameraController.CAPTURE_STATE_IDLE
        self.capture_status = "Capture state idle"

        self.camera_retrieve_state = [CameraController.RETRIEVE_STATE_IDLE] * (CameraController.MAX_CAMERAS+1)
        self.retrieve_state = CameraController.RETRIEVE_STATE_IDLE
        self.retrieve_status = "Retrieve state idle"

        self.render_state = CameraController.RENDER_STATE_IDLE
        self.render_status = "Render state idle"

        self.process_status = ""

        self.configure_time = 0.0
        self.capture_time = 0.0
        self.retrieve_time = 0.0
        self.render_time = 0.0

        self.render_path = os.path.join(self.output_path, "renders")
        self.image_path = os.path.join(self.output_path, "temp_image_files")
        self.saved_video_path = os.path.join(self.output_path, "saved_videos")
        self.current_image_path = self.image_path
        self.render_file = "None"
        self.last_render_file = "None"

        self.render_timestamp = ""
        self.render_loop = 1
        self.render_framerate = 24
        self.render_format = 'mp4'
        self.render_format_codec = {
            'mp4' : 'libx264',
            'mkv' : 'copy',
            'avi' : 'copy',
        }

        self.stagger_enable = False
        self.stagger_offset = 0

        self.render_process = None
        self.camera_monitor_enable = True
        self.camera_monitor_loop_ratio = 10
        self.camera_monitor_loop = self.camera_monitor_loop_ratio

        self.preview_enable = False
        self.preview_camera = 1
        self.preview_update = 1
        self.preview_time = 0.0

        self.preview_id = 0
        self.preview_image = ''

        default_preview_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "../static/img/testcard.jpg"))
        with open(default_preview_file, 'rb') as preview_file:
            self.preview_image = preview_file.read()

        self.preview_video = ''

        self.camera_max_ping_age = 4.0
        self.configure_timeout = 5.0
        self.capture_timeout = 5.0
        self.retrieve_timeout = 5.0
        self.render_timeout = 20.0

        self.capture_timeout_staggered = self.capture_timeout

        self.controller_period = 100
        self.controller = tornado.ioloop.PeriodicCallback(self.controller_callback, self.controller_period)
        self.controller.start()

        logging.info("State controller started")

        # Set the countdown state to False (countdown function is not executing)
        self.countdown_started = False

        # Set the countdown counter to 3
        self.capture_countdown_count = 3

        # Set the countdown interval to 1.0
        self.countdown_interval = 1.0

        # Set the capture countdown callback to be called every 1 second
        self.capture_countdown = tornado.ioloop.PeriodicCallback(self.capture_countdown_callback, self.countdown_interval * 1000)

        self.access_code = ''

    def controller_callback(self):

        self.handle_configure_state()
        self.handle_capture_state()
        self.handle_retrieve_state()
        self.handle_render_state()
        self.handle_preview_update()
        self.monitor_camera_state()

    def handle_configure_state(self):

        if self.configure_state == CameraController.CONFIGURE_STATE_CONFIGURING:

            num_cameras_configuring = self.get_num_enabled_in_state(CameraController.CONFIGURE_STATE_CONFIGURING, self.camera_configure_state)
            num_cameras_not_ready = self.get_num_enabled_in_state(CameraController.CONFIGURE_STATE_NOT_READY, self.camera_configure_state)
            configure_elapsed_time = time.time() - self.configure_time
            if num_cameras_configuring > 0:
                if configure_elapsed_time > self.configure_timeout:
                    self.configure_status = "Configure timed out with {} cameras in configuring state".format(num_cameras_configuring)
                    logging.error(self.configure_status)
                    self.configure_state = CameraController.CONFIGURE_STATE_NOT_READY
            elif num_cameras_not_ready > 0:
                if configure_elapsed_time > self.configure_timeout:
                    self.configure_status = "Configure timed out with {} cameras not ready".format(num_cameras_not_ready)
                    logging.error(self.configure_status)
                    self.configure_state = CameraController.CONFIGURE_STATE_NOT_READY
            else:
                self.configure_status = "Camera configuration completed OK after {:.3f} secs".format(configure_elapsed_time)
                logging.info(self.configure_status)
                self.configure_state = CameraController.CONFIGURE_STATE_READY

    def handle_capture_state(self):

        if self.capture_state == CameraController.CAPTURE_STATE_CAPTURING:

            num_cameras_capturing = self.get_num_enabled_in_state(CameraController.CAPTURE_STATE_CAPTURING, self.camera_capture_state)
            capture_elapsed_time = time.time() - self.capture_time
            if num_cameras_capturing > 0:
                self.capture_status = "Capture in progress on {} cameras".format(num_cameras_capturing)
                self.process_status = "The cameras are now capturing"
                if capture_elapsed_time > self.capture_timeout_staggered:
                    self.capture_status = "Captured timed out on {} cameras".format(num_cameras_capturing)
                    logging.error(self.capture_status)
                    self.process_status = "An error occurred while the cameras were capturing, please try capturing a video again"
                    self.capture_state = CameraController.CAPTURE_STATE_CAPTURING_FAILED
            else:
                self.capture_status = "Camera capture completed OK after {:.3f} secs".format(capture_elapsed_time)
                logging.info(self.capture_status)
                self.capture_state = CameraController.CAPTURE_STATE_CAPTURING_COMPLETED
                self.do_retrieve()
    
    def handle_retrieve_state(self):

        if self.retrieve_state == CameraController.RETRIEVE_STATE_RETRIEVING:
            
            num_cameras_retrieving = self.get_num_enabled_in_state(CameraController.RETRIEVE_STATE_RETRIEVING, self.camera_retrieve_state)
            retrieve_elapsed_time = time.time() - self.retrieve_time
            if num_cameras_retrieving > 0:
                if retrieve_elapsed_time > self.retrieve_timeout:
                    self.retrieve_status = "Retrieve timed out on {} cameras".format(num_cameras_retrieving)
                    logging.error(self.retrieve_status)
                    self.process_status = "An error occurred while retrieving the images, please try capturing a video again"
                    self.retrieve_state = CameraController.RETRIEVE_STATE_RETRIEVING_FAILED
            else:
                self.retrieve_status = "Image retrieve completed OK after {:.3f} secs".format(retrieve_elapsed_time)
                logging.info(self.retrieve_status)
                self.retrieve_state = CameraController.RETRIEVE_STATE_RETRIEVING_COMPLETED
                self.do_render()
    
    def handle_render_state(self):

        if self.render_state == CameraController.RENDER_STATE_RENDERING:

            render_state_poll = self.render_process.poll()
            render_elapsed_time = time.time() - self.retrieve_time

            if render_state_poll is None:
                if render_elapsed_time > (self.render_timeout * self.render_loop):
                    self.render_status = "Timeslice render timed out"
                    self.process_status = "An error occurred while creating your video, please try capturing a video again"
                    self.render_state = CameraController.RENDER_STATE_RENDERING_FAILED
            else:
                (render_stdout, render_stderr) = self.render_process.communicate()
                if render_state_poll == 0:
                    self.last_render_file = self.render_file
                    self.render_status = "Timeslice render completed OK after {:.3f} secs".format(render_elapsed_time)
                    logging.info(self.render_status)
                    self.render_state = CameraController.RENDER_STATE_RENDERING_COMPLETED
                    self.update_preview_video()              
                else:
                    self.render_status = "Timeslice render failed with return code {}".format(render_state_poll)
                    logging.error(self.render_status)
                    logging.error("Render output:\n{}\n{}".format(render_stdout, render_stderr))
                    self.render_state = CameraController.RENDER_STATE_RENDERING_FAILED

    def handle_preview_update(self):

        if self.preview_enable:

            if (time.time() - self.preview_time) > self.preview_update:
                logging.debug("Preview update fired")

                self.control_mcast_client.send("preview id={}".format(self.preview_camera))
                self.preview_time = time.time()

    def monitor_camera_state(self):

        # Run the camera periodic monitoring if enabled and a capture not in progress, as staggered capture means
        # the cameras don't reply to pings
        if self.camera_monitor_enable and self.capture_state != CameraController.CAPTURE_STATE_CAPTURING:
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

    def get_access_code(self):

        return self.access_code
    
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

    def get_capture_countdown_count(self):

        return self.capture_countdown_count

    def get_system_state(self):

        return self.system_state

    def get_system_status(self):

        return self.system_status

    def get_configure_state(self):

        return self.configure_state

    def get_configure_status(self):

        return self.configure_status

    def get_capture_state(self):

        return self.capture_state

    def get_capture_status(self):

        return self.capture_status

    def get_process_status(self):

        return self.process_status

    def get_camera_version_info(self):

        return self.camera_version_info[1:]

    def get_preview_image(self):

        return self.preview_image

    def get_preview_video(self):

        return self.preview_video

    def get_retrieve_state(self):

        return self.retrieve_state

    def get_render_state(self):
        
        return self.render_state

    def get_render_path(self):

        return self.render_path

    def get_last_render_file(self):

        return self.last_render_file

    def get_render_loop(self):

        return self.render_loop

    def get_stagger_enable(self):

        return self.stagger_enable

    def get_stagger_offset(self):

        return self.stagger_offset

    def set_capture_config(self, render_loop, stagger_enable, stagger_offset):

        self.render_loop = render_loop
        self.stagger_enable = stagger_enable
        self.stagger_offset = stagger_offset

    def set_camera_params(self, params):

        do_configure = 0

        config_changed = False

        for param in params:
            if param in self.camera_params:
                if self.camera_params[param] != params[param][-1]:
                    config_changed = True
                self.camera_params[param] = params[param][-1]
            elif param == 'configure':
                do_configure = True if params[param][-1] == '1' else False
            else:
                logging.warning("Attempting to set unknown camera parameter: {}".format(param))

        if config_changed:
            self.configure_state = CameraController.CONFIGURE_STATE_NOT_READY
            self.configure_status = "Configuration needs loading"

        if do_configure:

            self.configure_state = CameraController.CONFIGURE_STATE_CONFIGURING
            self.configure_time = time.time()
            self.configure_status = "Configuration in progress"

            for camera in range(1, CameraController.MAX_CAMERAS+1):
                if self.camera_enabled[camera]:
                    self.camera_configure_state[camera] = CameraController.CONFIGURE_STATE_CONFIGURING

            param_args = " ".join([ "=".join((param, val)) for param, val in self.camera_params.iteritems()])
            self.control_mcast_client.send("configure id=0 " + param_args)

    def get_camera_params(self, params):

        response = {}
        if params == []:
            response = self.camera_params
        else:
            for param in params:
                if param in self.camera_params:
                    response[param] = self.camera_params[param]
                else:
                    logging.warning("Unknown camera parameter requested: {}".format(param))

        return response

    def set_preview_mode(self, enable, camera, update):

        self.preview_enable = enable
        self.preview_camera = camera
        self.preview_update = update

    def get_preview_enable(self):

        return self.preview_enable

    def get_preview_camera(self):

        return self.preview_camera

    def get_preview_update(self):

        return self.preview_update

    def reset_state_values(self):

        """ Set capture, retrieve and render state to idle (0), and countdown count to 5 """

        self.capture_state = CameraController.CAPTURE_STATE_IDLE
        self.retrieve_state = CameraController.RETRIEVE_STATE_IDLE
        self.render_state = CameraController.RENDER_STATE_IDLE
        self.capture_countdown_count = 3
        self.preview_video = ''

    def do_capture_countdown(self):
        Removed with the countdown for the capture

        """ Set the countdown count to 5, launch the countdown and set the countdown state 
            to True if the countdown has not already been launched, otherwise do nothing.
        """
        
        if self.countdown_started == False:
            self.capture_countdown_count = 3
            self.capture_countdown.start()
            self.countdown_started = True
        else:
            pass

    def capture_countdown_callback(self):
        """ Decrement the countdown counter, and call the 'self.do_capture' function 
            and stop the periodic callback when the counter reaches 0.
        """

        logging.info("Capture coundown, count = {}".format(self.capture_countdown_count))
        self.capture_countdown_count = self.capture_countdown_count - 1
        
        if self.capture_countdown_count == 0:
            logging.info("Capture countdown triggering capture")
            self.do_capture(with_delay=True)
            self.capture_countdown.stop() 

            # Set countdown state to False
            self.countdown_started = False

    def do_capture(self, with_delay=False):

        # Define the output file location with a timestamped directory within the output path,
        # create the output directory if necessary and clear existing access code.

        if with_delay:
            time.sleep(0.30)

        self.access_code = ''

        self.render_timestamp = time.strftime("%Y%m%d-%H%M%S")

        self.current_image_path = os.path.join(self.image_path, "timeslice_{}".format(self.render_timestamp))

        logging.info("Writing image files to path {}".format(self.current_image_path))
        try:
            os.makedirs(self.current_image_path)
        except OSError, e:
            if not os.path.isdir(self.current_image_path):
                self.capture_status = "Failed to create image file path {} : {}".format(self.current_image_path, e)
                logging.error(self.capture_status)

        # Set the capture state to capturing, set the capture time
        self.capture_state = CameraController.CAPTURE_STATE_CAPTURING
        self.capture_time = time.time()
        self.capture_status = "Capture in progress"

        # Set state of enabled cameras to capturing
        for camera in range(1, CameraController.MAX_CAMERAS+1):
            if self.camera_enabled[camera]:
                self.camera_capture_state[camera] = CameraController.CAPTURE_STATE_CAPTURING

        # Calculate timeout dependent on whether staggered capture is enabled or not
        if self.stagger_enable:
            self.capture_timeout_staggered = self.capture_timeout + (CameraController.MAX_CAMERAS * ((1.0 * self.stagger_offset) / 1000.0))
        else:
            self.capture_timeout_staggered = self.capture_timeout

        stagger_enable = 1 if self.stagger_enable == True else 0
        self.control_mcast_client.send("capture id=0 stagger_enable={} stagger_offset={}".format(stagger_enable, self.stagger_offset))

        subprocess.Popen(shlex.split("/usr/bin/aplay -N /home/pi/timeslice/control_server/static/audio/shutter.wav"))

    def do_retrieve(self):

        # Set the capture state to retrieving, set the capture time
        self.retrieve_state = CameraController.RETRIEVE_STATE_RETRIEVING
        self.retrieve_time = time.time()
        self.retrieve_status = "Image retrieve in progress"
        self.process_status = "Please wait while I am retrieving the images from the cameras"

        # Set state of enabled cameras to retrieving
        for camera in range(1, CameraController.MAX_CAMERAS+1):
            if self.camera_enabled[camera]:
                self.camera_retrieve_state[camera] = CameraController.RETRIEVE_STATE_RETRIEVING
                logging.info("camera_retrieve_state = {}".format(self.camera_retrieve_state))

        self.control_mcast_client.send("retrieve id=0")

    def do_render(self):

        self.render_state = CameraController.RENDER_STATE_RENDERING
        self.render_time = time.time()
        self.render_status = "Timeslice render in progress"
        self.process_status = "Images retrieved successfully, I am now creating your video"

        # Squash file list to ensure files are contiguously numbered

        src_files = sorted(glob.glob(os.path.join(self.current_image_path, "image_*.jpg")))
        num_src_files = len(src_files)
        squashed_files = []
        num_squashed = 0
        dst_idx = 1

        for src_file in src_files:
            dst_file = (os.path.join(self.current_image_path, "image_{:03d}.jpg".format(dst_idx)))
            if src_file != dst_file:
                num_squashed += 1
                os.rename(src_file, dst_file)
            squashed_files.append(dst_file)
            dst_idx += 1

        logging.info("Squashed {} image files out of {} in render path {}".format(num_squashed, num_src_files, self.current_image_path))

        # Copy image files in order to generate the correct number of loops for rendering

        dst_idx = len(squashed_files) + 1

        for loop in range(self.render_loop-1):
            for src_file in squashed_files:
                dst_file = os.path.join(self.current_image_path, "image_{:03d}.jpg".format(dst_idx))
                shutil.copy2(src_file, dst_file)
                dst_idx += 1

        logging.info("Created a total of {} image files from {} for {} render loops at path {}".format(
                    dst_idx-1, num_src_files, self.render_loop, self.current_image_path))

        input_file_pattern = os.path.join(self.current_image_path, "image_%03d.jpg")
        self.render_file = os.path.join(self.render_path, "timeslice_{}.{}".format(self.render_timestamp, self.render_format))

        render_cmd = "ffmpeg -framerate {} -i \'{}\' -codec {} -y {}".format(
                        self.render_framerate, input_file_pattern, self.render_format_codec[self.render_format], self.render_file)
        logging.info("Launching render process with command: {}".format(render_cmd))

        self.render_process = subprocess.Popen(shlex.split(render_cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def do_save(self):

        """ Call the 'self.reset_state_values' function, generate an alphanumeric 
            access code and save the rendered file to the 'saved_videos' folder.
            Exclude 0's and O's from the access code to avoid confusion.
        """

        self.reset_state_values()

        access_code_length = 7
        chars = string.ascii_uppercase + string.digits
        chars = ''.join(sorted(set(chars) - set('0O')))

        self.access_code = ''.join(random.choice(chars) for _ in range(access_code_length))

        save_render_file_name = os.path.join(self.saved_video_path, "{}.mp4".format(self.access_code))
        shutil.copy2(self.render_file, save_render_file_name)
        logging.info("Saved render file as {}.mp4 in save render path {}".format(self.access_code, self.saved_video_path))

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

            self.camera_capture_state[id] = CameraController.CAPTURE_STATE_CAPTURING_COMPLETED

    def update_camera_configure_state(self, id, did_ack):

        if id < 1 or id > CameraController.MAX_CAMERAS:
            logging.warning("Got camera configure response for illegal ID: {}".format(id))
        else:
            if self.camera_configure_state[id] != CameraController.CONFIGURE_STATE_CONFIGURING:
                logging.warning("Got configure response for camera ID {} when not in configuring state".format(id))
            elif not did_ack:
                logging.warning("Camera ID {} responded with no-acknowledge for capture command".format(id))
                self.camera_configure_state[id] = CameraController.CONFIGURE_STATE_NOT_READY
            else:
                self.camera_configure_state[id] = CameraController.CONFIGURE_STATE_READY

    def update_camera_retrieve_state(self, id, did_ack, image_data):

        if id < 0 or id > CameraController.MAX_CAMERAS:
            logging.warning("Got camera retrieve response for illegal ID: {}".format(id))
        else:
            if self.camera_retrieve_state[id] != CameraController.RETRIEVE_STATE_RETRIEVING:
                logging.warning("Got retrieve response for camera ID {} when not in retrieving state".format(id))
            elif not did_ack:
                logging.warning("Camera ID {} responded with no-acknowledge for retrieve command".format(id))

            self.camera_retrieve_state[id] = CameraController.RETRIEVE_STATE_RETRIEVING_COMPLETED

            if image_data is not None and len(image_data) > 0:
                image_file_name = os.path.join(self.current_image_path, "image_{:03d}.jpg".format(id))
                image_file = open(image_file_name, 'wb')
                image_file.write(image_data)
                image_file.close()
                logging.info("Wrote image data for camera {} to file {}".format(id, image_file_name))

    def update_preview_image(self, id, image_data):

        self.preview_image_id = id
        self.preview_image = image_data

    def update_preview_video(self):
        """ Open the rendered file in binary mode and assign its data to 'self.preview_video'. """

        video_file = self.render_file
        logging.info("video_file = {}".format(video_file))
        with open(video_file, 'rb') as preview_video_file:
            self.preview_video = preview_video_file.read()

    def do_calibrate(self, camera):

        self.control_mcast_client.send("calibrate id={}".format(camera))
