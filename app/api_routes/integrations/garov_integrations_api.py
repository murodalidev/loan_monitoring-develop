from fastapi import APIRouter, Depends
from app.db.connect_db import SessionManager
from ...services.loan_monitoring.integrations import garov_integrations
from ...schemas.integrations import Garov_notary_ban_list, Garov_notary_ban, Garov_notary_ban_cancel
from ...config.logs_config import info_logger
from app.middleware.auth_file import AuthHandler

auth_handler = AuthHandler()



router = APIRouter(
    prefix = "/integrations/garov", tags=["GAROV"]
)

@router.post('/v1/notary/ban/list')
def garov_notary_ban_list(request:Garov_notary_ban_list, user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        response = garov_integrations.garov_notary_ban_list(request, user.id, db_session)
    info_logger.info("User %s requested garov_notary_ban_list", user.id)
    
    return response


@router.post('/v1/notary/ban')
def garov_notary_ban(request:Garov_notary_ban, user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        response = garov_integrations.garov_notary_ban(request, user.id, db_session)
    info_logger.info("User %s requested garov_notary_ban", user.id)  
    
    return response


@router.post('/v1/notary/ban/cancel')
def garov_notary_ban_cancel(request:Garov_notary_ban_cancel, user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        response = garov_integrations.garov_notary_ban_cancel(request, user.id, db_session)
    info_logger.info("User %s requested garov_notary_ban_cancel", user.id)
    
    return response


@router.get('/v1/notary/subject-type')
def get_notary_subject_type(user=Depends(auth_handler.auth_wrapper)):
    response = garov_integrations.get_notary_subject_type()
    info_logger.info("User %s requested garov_get_notary_subject_type", user.id)
    
    return response


@router.get('/v1/notary/property-type')
def get_notary_property_type(user=Depends(auth_handler.auth_wrapper)):
    response = garov_integrations.get_notary_property_type()
    info_logger.info("User %s requested get_notary_property_type", user.id)
    
    return response


@router.get('/v1/notary/doc-type')
def get_notary_document_type(user=Depends(auth_handler.auth_wrapper)):
    response = garov_integrations.get_notary_document_type()
    info_logger.info("User %s requested get_notary_document_type", user.id) 
    
    return response