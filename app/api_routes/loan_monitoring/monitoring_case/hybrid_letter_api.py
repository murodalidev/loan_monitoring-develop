from fastapi import APIRouter, UploadFile
from app.services.loan_monitoring.monitoring_case.hybrid_letter import hybrid_letter, cron_hybrid_letter
from app.db.connect_db import SessionManager
from ....services.websocket.create_websocket import manager
from fastapi import BackgroundTasks
from ....common.save_file import save_file
from ....common import common_handler
from app.middleware.auth_file import AuthHandler
auth_handler = AuthHandler()
from ....services.loan_monitoring.loan_case import loan_case_crud
from ....schemas.problems_case_schemas import  GenerateLetter, SendLetter, AppendLetter


router = APIRouter(
    prefix = "/hybrid_letter", tags=["Hybrid Letter"]
)

@router.post('/v1/generate-letter')
def letter_generate(request:GenerateLetter):
    with SessionManager() as db_session:
        response = hybrid_letter.generate_letter(request,db_session)
    return response



@router.post('/v1/send-letter')
def portrfolio(request:SendLetter):
    with SessionManager() as db_session:
        response = hybrid_letter.send_letter(request, db_session)
        #response = hybrid_letter.send_letter,request,db_session)
    return response

@router.post('/v1/append-exist-letter')
async def append(request: AppendLetter, letter: UploadFile = None):
    with SessionManager() as db_session:
        response = common_handler.handle_error(hybrid_letter.append_letter,request, letter, db_session)
    return response

@router.get('/v1/check-status/by-id')
def portrfolio(id:int):
    with SessionManager() as db_session:
        response = common_handler.handle_error(hybrid_letter.get_letter_by_id, id, db_session)
    return response




@router.get('/v1/send-letters-schedule')
def check_expired_days(back_task: BackgroundTasks):
    
    with SessionManager() as db_session:
        #back_task.add_task(cron_hybrid_letter.cron_send_letter_schedule,db_session)
        cron_hybrid_letter.cron_send_letter_schedule(35,44, db_session)
    
    with SessionManager() as db_session:
        #back_task.add_task(cron_hybrid_letter.cron_send_letter_schedule,db_session)
        cron_hybrid_letter.cron_send_letter_schedule(45,55,db_session)
    
        return 'OK'



@router.get('/v1/get-detail')
def portrfolio(kad_case_id:int, general_task_id:int):
    with SessionManager() as db_session:
        response = common_handler.handle_error(hybrid_letter.get_letter_by_kad_case_id, kad_case_id, general_task_id, db_session)
    return response

@router.get('/v1/get-detail/by-portfolio')
def get_letter_by_portfolio(loan_portfolio_id:int, general_task_id:int):
    with SessionManager() as db_session:
        response = common_handler.handle_error(hybrid_letter.get_letter_by_portfolio_id, loan_portfolio_id, general_task_id, db_session)
    return response



@router.get('/v1/get-details-to-send')
def portrfolio(loan_id:int=None):
    with SessionManager() as db_session:
        response = hybrid_letter.get_details_for_send(loan_id, db_session)
    return response


@router.get('/v1/get/base64')
def get_areas(letter_id:int):
    with SessionManager() as db_session:
        response = hybrid_letter.get_base64(letter_id, db_session)
    return response



@router.get('/v1/get/areas')
def get_areas():
    with SessionManager() as db_session:
        response = hybrid_letter.get_areas()
    return response


@router.get('/v1/get/regions')
def get_areas():
    with SessionManager() as db_session:
        response = hybrid_letter.get_regions()
    return response



@router.get('/v1/get-post-codes')
def portrfolio(id:int):
    with SessionManager() as db_session:
        response = hybrid_letter.get_post_code_by_loan_portfolio_id(id,db_session)
    return response




@router.get('/v1/match-post-codes-to-regions')
def match_post_codes():
    with SessionManager() as db_session:
        response = hybrid_letter.match_post_codes_to_region(db_session)
    return response