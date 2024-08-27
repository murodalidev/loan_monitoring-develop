from fastapi import HTTPException
import logging
logger = logging.getLogger(__name__)


def is_empty(object, code, message):
    if object is not None:
        logger.error(message)
        raise HTTPException(status_code=code, detail=message)
    
    
def is_empty_list(object, code, message):
    if object != []:
        logger.error(message)
        raise HTTPException(status_code=code, detail=message)
      
    
def is_exists(object, code, message):
    if object is None:
        logger.error(message)
        raise HTTPException(status_code=code, detail=message)
    
    
    
def warning(code, message):
    logger.error(message)
    raise HTTPException(status_code=code, detail=message)