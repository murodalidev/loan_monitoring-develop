import datetime
from fastapi import APIRouter, Request, Response
import logging
from sqlalchemy.sql import text
logger = logging.getLogger(__name__)
import time
router = APIRouter(
    prefix = "", tags=['PING']
)


#Проверка связи
@router.get('/ping')
async def read_root():
    #date_object = datetime.datetime.strptime('23.08.2023', '%d.%m.%Y').date().replace('-','.')
    time.sleep(5)
    return '1234'



