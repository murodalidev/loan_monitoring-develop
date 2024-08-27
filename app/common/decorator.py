import time
from ..config.logs_config import cron_logger

def measure_time(func):
    def wrapper(*args, **kwargs):
        cron_logger.info(f'Started {func.__name__}')
        start_timer = time.time()
        
        func(*args, **kwargs)
        
        end_timer = time.time()
        res = end_timer - start_timer
        final_res = res / 60
        cron_logger.info(f'Execution time: {final_res} minutes')
        cron_logger.info(f'Finished {func.__name__}')
    return wrapper