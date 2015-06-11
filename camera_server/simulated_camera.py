import logger

class SimulatedCamera(object):

    def __init__(self):

        self.logger = logger.get_logger()

        self.logger.debug("Using simulated camera object")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
