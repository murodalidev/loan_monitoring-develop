from fastapi import APIRouter
from app.db.connect_db import SessionManager
from app.db.oracle_connect import OracleSessionManager
from ...services.loan_monitoring.integrations import playmobile_integrations


router = APIRouter(
    prefix = "/integrations", tags=["PlayMobile"]
)

@router.post('playmobile/v1/send_message')
def send_message(phone_number: str=None, message: str=None):
  response = playmobile_integrations.send_sms_playmobile(phone_number, message)
  return response


@router.post('playmobile/v1/send-to-all-clients')
def send_message():
  with SessionManager() as db_session:
    response = playmobile_integrations.send_sms_to_clients(db_session)
  return response