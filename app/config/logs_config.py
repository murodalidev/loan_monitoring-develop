import logging
from logging.handlers import TimedRotatingFileHandler



INFO_LOG_FILE = 'logs/info/info_log.log'
CRON_LOG_FILE = 'logs/cron/cron_log.log'
ERROR_LOG_FILE = 'logs/error/error_log.log'
LOG_LEVEL_INFO = logging.INFO
LOG_LEVEL_ERROR = logging.ERROR

class CronLogger():
    @staticmethod
    def setup_cron_logging():
        logger = logging.getLogger('CRON_LOGGING')
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(u'[%(asctime)s] - %(filename)s:%(lineno)d #%(levelname)-8s  - %(name)s - %(message)s')
        
        # Обработчик для логирования информационных сообщений
        info_handler = get_timed_rotating_file_handler(CRON_LOG_FILE, LOG_LEVEL_INFO, formatter)
        logger.addHandler(info_handler)
        return logger
        
class InfoLogger():
    @staticmethod
    def setup_info_logging():
        logger = logging.getLogger('INFO_LOGGING')
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(u'[%(asctime)s] - %(filename)s:%(lineno)d #%(levelname)-8s  - %(name)s - %(message)s')
        
        # Обработчик для логирования информационных сообщений
        info_handler = get_timed_rotating_file_handler(INFO_LOG_FILE, LOG_LEVEL_INFO, formatter)
        logger.addHandler(info_handler)
        return logger



def get_timed_rotating_file_handler(file_path, log_level, formatter):
    handler = TimedRotatingFileHandler(file_path, when="midnight", interval=1, encoding='utf8', backupCount=30)
    handler.suffix = "%Y-%m-%d_%H-%M-%S"
    handler.setFormatter(formatter)
    handler.setLevel(log_level)
    return handler


cron_logger = CronLogger().setup_cron_logging()

info_logger = InfoLogger().setup_info_logging()