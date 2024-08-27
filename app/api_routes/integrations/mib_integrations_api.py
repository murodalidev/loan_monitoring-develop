from fastapi import APIRouter, Depends
from app.db.connect_db import SessionManager
from ...services.loan_monitoring.integrations import mib_integrations
from ...schemas.integrations import MIB_debtors_info
from ...config.logs_config import info_logger
from app.middleware.auth_file import AuthHandler

auth_handler = AuthHandler()



router = APIRouter(
    prefix = "/integrations/mib", tags=["MIB"]
)

@router.post('/v1/debtors/pinfl')
def information_debtors_pinfl(request:MIB_debtors_info, user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        response = mib_integrations.information_debtors_pinfl(request, user.id, db_session)
    info_logger.info("User %s requested bux balance by form1", user.id)
    
    return response


@router.post('/v1/debtors/stir')
def information_debtors_pinfl(request:MIB_debtors_info, user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        response = mib_integrations.information_debtors_stir(request, user.id, db_session)
    info_logger.info("User %s requested bux balance by form1", user.id)
    
    return response


@router.post('/v1/actions/pinfl')
def information_actions_pinfl(request:MIB_debtors_info, user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        response = mib_integrations.information_actions_pinfl(request, user.id, db_session)
    info_logger.info("User %s requested bux balance by form1", user.id)
    
    return response


@router.post('/v1/actions/stir')
def information_actions_stir(request:MIB_debtors_info, user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        response = mib_integrations.information_actions_stir(request, user.id, db_session)
    info_logger.info("User %s requested bux balance by form1", user.id)
    
    return response