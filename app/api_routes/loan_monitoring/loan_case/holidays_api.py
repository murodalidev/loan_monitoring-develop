from fastapi import APIRouter, Depends
import logging
from app.db.connect_db import SessionManager
from app.middleware.auth_file import AuthHandler
from ....schemas.user_schemas import Holiday
from app.services.loan_monitoring.monitoring_case import script_date_holidays

auth_handler = AuthHandler()
router = APIRouter(
    prefix = "/holidays", tags=["Holidays"]
)

@router.get('/v1/read/all')
def holiday_get_all():
    with SessionManager() as db_session:
        branches = script_date_holidays.get_all_holidays(db_session)
    return branches

@router.post('/v1/add')
def holiday_add(request:Holiday):
    with SessionManager() as db_session:
        status = script_date_holidays.add_holiday(request, db_session)   
    return status

# @router.put('/v1/update/{id}')
# def holiday_update(id:int, holiday:str=None):
#     with SessionManager() as db_session:
#         status = script_date_holidays.update_holiday(id, holiday, db_session)
#     return status

@router.delete('/v1/delete/{id}')
def holiday_delete(id:int):
    with SessionManager() as db_session:
        status = script_date_holidays.delete_holiday(id,db_session)
    return status