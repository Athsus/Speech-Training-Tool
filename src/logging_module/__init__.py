import sys

from src.logging_module.event_logger import EventLogger


def apply_logger():

    logger = EventLogger()
    sys.stdout = logger.info
    sys.stderr = logger.error


