import logger
import os

class PiCameraError(Exception):
    """
    Base class for PiCamera errors.
    """


class PiCameraRuntimeError(PiCameraError, RuntimeError):
    """
    Raised when an invalid sequence of operations is attempted with a
    :class:`~picamera.camera.PiCamera` object.
    """

class SimulatedCamera(object):

    camera_id = 0

    @classmethod
    def set_camera_id(cls, camera_id):
        cls.camera_id = camera_id

    def __init__(self):

        self.logger = logger.get_logger()
        self.logger.debug("Using simulated camera object with ID {}".format(SimulatedCamera.camera_id))

        self.image = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def capture(self, output, format=None, use_video_port=False, resize=None, splitter_port=0, **options):

        source_path =  os.path.dirname(os.path.realpath(__file__))
        testcard_path = os.path.join(source_path, "testcards", '{:02d}.missing.jpg'.format(SimulatedCamera.camera_id))

        try:
            testcard_file = open(testcard_path, 'r')
            self.image = testcard_file.read()
            self.logger.debug("Read test card image file {} OK (length = {})".format(testcard_path, len(self.image)))
        except IOError, e:
            self.logger.error("Unable to read test card image file: {}".format(e))
            raise PiCameraRuntimeError("Unable to read test card image file: {}".format(e))
