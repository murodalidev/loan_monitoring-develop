from fastapi import APIRouter, Depends
from app.db.connect_db import SessionManager
from ...services.adliya import check_family_service
from ...services.adliya import check_notarial_ban
from ...schemas.adliya_schemas import Check_Family, Notarial_Ban, Notarial_Ban_By_Subject

from app.middleware.auth_file import AuthHandler
auth_handler = AuthHandler()
import logging
logger = logging.getLogger(__name__)


router = APIRouter(
    prefix = "/adliya", tags=["Adliya API"]
)


@router.post('/v1/check-family')
def check_familiy(request:Check_Family, user=Depends(auth_handler.auth_wrapper)):
    logger.info('User is requiring adliya check-family method.')
    with SessionManager() as db_session:
        response = check_family_service.check_family(request, user.id, db_session)
    return response


@router.post('/v1/notarial-ban')
def notarial_ban(request:Notarial_Ban, user=Depends(auth_handler.auth_wrapper)):
    logger.info('User is requiring adliya notarial-ban method.')
    with SessionManager() as db_session:
        response = check_notarial_ban.notarial_ban(request, user.id, db_session)
    return response


@router.post('/v1/notarial-ban-by-subject')
def notarial_ban_by_subject(request:Notarial_Ban_By_Subject, user=Depends(auth_handler.auth_wrapper)):
    logger.info('User is requiring adliya notarial-ban-by-subject method.')
    with SessionManager() as db_session:
        response = check_notarial_ban.notarial_ban_by_subject(request, user.id, db_session)
    return response
