from ..config.logs_config import info_logger
from fastapi import HTTPException





def handle_error(func, *args):
    
    try:
        response = func(*args)
    except Exception as e:
        info_logger.info(e)
        raise HTTPException(status_code=403, detail=str(e))
    
    return response