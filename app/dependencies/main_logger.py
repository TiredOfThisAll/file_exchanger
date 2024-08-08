from app.dependencies.base_logger import BaseLogger

class MainLogger:
    singleton = BaseLogger()

    @staticmethod
    def debug(msg):
        MainLogger.singleton.logger.debug(msg)

    @staticmethod
    def info(msg):
        MainLogger.singleton.logger.info(msg)
    
    @staticmethod
    def warning(msg):
        MainLogger.singleton.logger.warning(msg)
    
    @staticmethod
    def error(msg):
        MainLogger.singleton.logger.error(msg)
    
    @staticmethod
    def critical(msg):
        MainLogger.singleton.logger.critical(msg)
