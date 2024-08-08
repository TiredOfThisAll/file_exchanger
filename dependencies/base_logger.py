import logging
import os

from settings.config import CONFIG

class BaseLogger:
    def __init__(self):
        self.logger = logging.getLogger("file_logger")
        logging.basicConfig(
            filename=os.path.join(CONFIG.LOGS_PATH, CONFIG.LOGS_FILE_NAME),
            encoding='utf-8',
            level=logging.DEBUG
        )

    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)

    def critical(self, msg):
        self.logger.critical(msg)
