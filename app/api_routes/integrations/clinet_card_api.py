from fastapi import APIRouter
from app.db.oracle_connect import OracleSessionManager
from fastapi import BackgroundTasks
from ...services.loan_monitoring.integrations import client_card
import logging
logger = logging.getLogger(__name__)
router = APIRouter(
    prefix = "/account_turnover", tags=["Account Turnover"]
)

# @router.get('/v1/load/accounts')
# def load_all_accounts():
#     with OracleSessionManager() as orc_session:
#             result = client_card.load_client_data(orc_session)
#     return result



@router.get('/v1/load/schedules')
def load_schedules():
    with OracleSessionManager() as orc_session:
            result = client_card.load_loan_schedule(orc_session)
    return result