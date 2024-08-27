from fastapi import APIRouter, Depends
from app.db.connect_db import SessionManager
from ....common import common_handler
from ....services.loan_monitoring.loan_porfolio.loan_portfolio_schedule_service import get_all_schedule, get_all_phone
import json
from app.middleware.auth_file import AuthHandler


auth_handler = AuthHandler()
router = APIRouter(
    prefix = "/portfolio-schedule", tags=["Loan Porfolio Schedule"]
)


@router.get('v1/get/all')
def protfolio_schedule(offset: int, size: int):
    with SessionManager() as db_session:
        response = common_handler.handle_error(get_all_schedule, offset, size, db_session)
    return response

@router.get('v1/get/phone/all')
def protfolio_phone(offset: int, size: int):
    with SessionManager() as db_session:
        response = common_handler.handle_error(get_all_phone, offset, size, db_session)
    return response