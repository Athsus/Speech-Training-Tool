import sys

from src.logging_handler.event_logger import EventLogger


def apply_logger():

    logger = EventLogger()
    sys.stdout = logger.info
    sys.stderr = logger.error


