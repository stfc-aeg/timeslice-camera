class PiCameraError(Exception):
    """
    Base class for PiCamera errors.
    """

class PiCameraRuntimeError(PiCameraError, RuntimeError):
    """
    Raised when an invalid sequence of operations is attempted with a
    :class:`~picamera.camera.PiCamera` object.
    """
