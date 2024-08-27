from fastapi import APIRouter, Depends, UploadFile, Body
from ....services.loan_monitoring.problems_case import state_chains
from ....services.loan_monitoring.problems_case.problems_assets import problems_assets_get
from ....services.loan_monitoring.problems_case.auction import attach_files
from ....services.loan_monitoring.problems_case.mib_ended import attach_files as mib_attach_files
from ....services.loan_monitoring.problems_case.mib_ended import accept_or_rework_mib_ended
from ....services.loan_monitoring.problems_case.auction import accept_or_rework_auction
from ....services.loan_monitoring.problems_case import problems_state_notification, problems_case_crud, cron_problems_case, problems_balance_turnover_crud, non_targeted_case, out_of_balance_case
from ....services.loan_monitoring.juridical_case import juridical_case_crud
from app.db.connect_db import SessionManager
from typing import Union, List
from ....services.websocket.create_websocket import manager
import json
from ....common.save_file import save_file, save_multiple_files
from app.middleware.auth_file import AuthHandler
auth_handler = AuthHandler()
from ....services.loan_monitoring.loan_case import loan_case_crud
from ....schemas.problems_case_schemas import AcceptOrReworkAuction, AcceptOrReworkMibData, ProblemsCaseSend, ReplyToNewLoan, SendNonTargetStateFiles, SendAuctionFiles,  SendMibFiles
from ....schemas.problems_case_schemas import ProblemsCaseAppoint, AppointSendLetter, GenerateLetter, SendLetter, CloseProblemsCase,ProblemsCaseSendJuridical, SendLetterToNonTarget
router = APIRouter(
    prefix = "/problems-case", tags=["Problems Case"]
)




@router.post('/v1/appoint-responsible')
async def portrfolio(request:ProblemsCaseAppoint):
    with SessionManager() as db_session:
        response = problems_case_crud.appoint_responsible_for_problems_monitoring(request,db_session)
        message = {'notification_message':'appoint responsible', 'type':'problem'}
        await manager.send_direct_message(request.to_user,json.dumps(message))
    return response


# @router.get('/v1/get/all')
# def portrfolio(user=Depends(auth_handler.auth_wrapper)):
#     with SessionManager() as db_session:
#         db_session.add(user)
#         response = problems_case_crud.get_all_problems_case(user.id, db_session)
#     return {"loan_case":response}






@router.post('/v1/send-to-juridical')
async def portrfolio(request:ProblemsCaseSendJuridical= Body(...), files: List[UploadFile] = None, user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        file_path = [save_file(file) for file in files]
        db_session.add(user)
        response = juridical_case_crud.send_to_juridical(request, user.department,file_path, db_session)
        message = {'notification_message':'send to juridical', 'type':'juridical'}
        await manager.local_broadcast(response,json.dumps(message))
    return 'OK'



@router.post('/v1/close')
async def portrfolio(request:CloseProblemsCase):
    with SessionManager() as db_session:
        response = problems_case_crud.close_problems_case(request,db_session)
        message = {'notification_message':'close juridical', 'type':'loan'}
        await manager.send_direct_message(response,json.dumps(message))
    return 'OK'


@router.post('/v2/close')
async def portrfolio(request:CloseProblemsCase):
    with SessionManager() as db_session:
        response = problems_case_crud.close_problems_casev2(request,db_session)
        message = {'notification_message':'close juridical', 'type':'loan'}
        await manager.send_direct_message(response,json.dumps(message))
    return 'OK'


@router.post('/v1/reply-to-new-loan')
async def portrfolio(request:ReplyToNewLoan= Body(...), files: List[UploadFile] = None):
    with SessionManager() as db_session:
        file_path = [save_file(file) for file in files]
        response = problems_case_crud.reply_to_new_juridical_case(request,file_path,db_session)
        message = {'notification_message':'reply to new loan', 'type':'juridical'}
        await manager.send_direct_message(response, json.dumps(message))
    return response


@router.get('/v1/get/history')
def portrfolio(problems_case_id:int, general_task_id:int):
    with SessionManager() as db_session:
        response = problems_case_crud.get_problems_case_history(problems_case_id,general_task_id, db_session)
    return response




@router.get('/v1/problems-monitoring/get')
def portrfolio(problems_case_id:int):
    with SessionManager() as db_session:
        response = problems_case_crud.get_problems_monitoring(problems_case_id, db_session)
    return response



@router.get('/v1/problems-monitoring/set-task/send-juridic')
def set_to_juridic():
    with SessionManager() as db_session:
        response = cron_problems_case.send_to_juridical_notification(db_session)
    return response


@router.get('/v1/get/all')
def problems_case(size:int, page:int, region_id:int=None, local_code_id:int=None, loan_id:int=None, client_name:str=None, 
               is_target:int=None, product_type:int=None, currency_id:int=None, state_chain:int=None, client_type:str=None, main_responsible:int=None, client_code:int=None, task_status_id:int=None,
               second_responsible:int=None,
               user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        db_session.add(user)
        response = problems_case_crud.get_all_problems_case(size, page, region_id, local_code_id, loan_id, client_name, is_target, task_status_id,
                                                    product_type, state_chain, client_type, client_code, currency_id, main_responsible, user, second_responsible,
                                                    user.department, db_session)
    return response




@router.get('/v1/get/details')
def problems_case(problem_case_id:int):
    with SessionManager() as db_session:
        response = problems_case_crud.get_problems_case_details(problem_case_id, db_session)
    return response




@router.get('/v1/get/non-target/all')
def problems_case(size:int, page:int, region_id:int=None, local_code_id:int=None, loan_id:int=None, state_chain:int=None, client_name:str=None, 
               is_target:int=None, product_type:int=None, client_type:str=None, total_overdue_asc_desc:int=None, client_code:int=None, expired:bool=None,
               main_responsible:int=None, second_responsible:int=None,
               user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        db_session.add(user)
        response = non_targeted_case.get_all_non_target(size, page, region_id, local_code_id, loan_id, state_chain, client_name, is_target,
                                                    product_type, client_type, client_code, total_overdue_asc_desc, user,
                                                    main_responsible, second_responsible, user.department, db_session)
    return response




@router.post('/v1/send-letter-to-non-target')
def send_letters_to_non_target(request:SendLetterToNonTarget= Body(...), non_target_letter: List[UploadFile] = None):
    with SessionManager() as db_session:
        file_path = save_multiple_files(directory='non_target_files', non_target_letter = non_target_letter)
        response = non_targeted_case.send_letter_to_non_target(request, file_path, db_session)
    return response


@router.get('/v1/get/non-target-letter')
def main_page_data(problems_case_id:int=None):
    with SessionManager() as db_session:
        response = non_targeted_case.get_letter_by_problems_case_id(problems_case_id, db_session)
    return response





@router.get('/v1/get/turnover')
def problems_case(size:int, page:int, region_id:int=None, local_code_id:int=None, loan_id:int=None, state_chain:int=None, client_name:str=None, currency_id:int=None, product_type:int=None, client_type:str=None,
                  main_responsible:int=None, second_responsible:int=None, task_status:int=None, user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        db_session.add(user)
        response = problems_balance_turnover_crud.get_problems_all_turnover(size, page, user, region_id,local_code_id,client_name, currency_id, loan_id, task_status, state_chain, product_type, client_type,
                                                                            main_responsible, second_responsible, db_session)
    return response


@router.get('/v1/get/main-page-data')
def main_page_data():
    with SessionManager() as db_session:
        response = problems_case_crud.get_promblems_data_for_main_page(db_session)
    return response


@router.get('/v1/get/out-of-balance')
def problems_case(size:int, page:int, region_id:int=None, local_code_id:int=None, loan_id:int=None, client_name:str=None, task_status_id:int=None, state_chain:int=None, product_type:int=None, client_type:str=None,
                  main_responsible:int=None, second_responsible:int=None, user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        db_session.add(user)
        response = out_of_balance_case.get_out_of_balance_all_turnover(size, page, user, region_id,local_code_id,client_name, loan_id, task_status_id, state_chain,  product_type, 
                                                                        main_responsible, second_responsible, client_type, db_session)
    return response




@router.get('/v1/get/assets')
def get_assets(size:int, page:int, region_id:int=None, local_code_id:int=None, loan_id:int=None, client_name:str=None, product_type:int=None, client_type:str=None,
                  main_responsible:int=None, second_responsible:int=None, user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        db_session.add(user)
        response = problems_assets_get.get_problems_assets(size, page, user, region_id,local_code_id,client_name, loan_id, product_type, client_type,
                                                                            main_responsible, second_responsible, db_session)
    return response


@router.get('/v1/get-assets-status')
def get_loan_statuses():
    with SessionManager() as db_session:
        response = problems_assets_get.get_assets_status(db_session)
    return response



@router.get('/v1/get/problem-states')
def main_page_data():
    with SessionManager() as db_session:
        response = state_chains.get_problem_states(db_session)
    return response




@router.post('/non-target-state/v1/send-files')
def send_non_target_files(request:SendNonTargetStateFiles= Body(...), non_target_state_files: List[UploadFile] = None):
    with SessionManager() as db_session:
        file_path = save_multiple_files(directory='non_target_state_files', non_target_state_files = non_target_state_files)
        response = non_targeted_case.upload_non_target_state_files(request, file_path, db_session)
    return response


@router.get('/v1/get/non-target-states')
def get_non_target_state_types(problems_case_id:int=None, non_target_type_id:int=None):
    with SessionManager() as db_session:
        response = non_targeted_case.get_non_target_state(problems_case_id, non_target_type_id,db_session)
    return response



@router.get('/v1/get/non-target-state-types')
def get_non_target_state_types():
    with SessionManager() as db_session:
        response = non_targeted_case.get_non_target_state_types(db_session)
    return response



@router.post('/auction/v1/send-files')
def send_auction_files(request:SendAuctionFiles= Body(...), auction_files: List[UploadFile] = None):
    with SessionManager() as db_session:
        file_path = save_multiple_files(directory='auction_files', auction_files = auction_files)
        response = attach_files.upload_auction_files(request, file_path, db_session)
    return response

@router.post('/auction/v1/accept-or-rework')
async def accept_or_rework_auction_api(request:AcceptOrReworkAuction):
    with SessionManager() as db_session:
        response = accept_or_rework_auction.accept_or_rework_auction_data(request, db_session)
        message = {'notification_message':'accept or rework', 'type':'juridical'}
        await manager.send_direct_message(request.to_user,json.dumps(message))
    return response




@router.get('/v1/get/auctions')
def get_auction(problems_case_id:int=None, auction_type_id:int=None):
    with SessionManager() as db_session:
        response = attach_files.get_auction(problems_case_id, auction_type_id,db_session)
    return response



@router.get('/v1/get/auction-types')
def get_auction_types():
    with SessionManager() as db_session:
        response = attach_files.get_auction_types(db_session)
    return response




@router.post('/mib/v1/send-files')
def send_mib_files(request:SendMibFiles= Body(...), mib_ended_files: List[UploadFile] = None):
    with SessionManager() as db_session:
        file_path = save_multiple_files(directory='mib_ended_files', mib_ended_files = mib_ended_files)
        response = mib_attach_files.upload_mib_files(request, file_path, db_session)
    return response


@router.post('/mib/v1/accept-or-rework')
async def accept_or_rework_mib(request:AcceptOrReworkMibData):
    with SessionManager() as db_session:
        response = accept_or_rework_mib_ended.accept_or_rework_mib_ended_data(request, db_session)
        message = {'notification_message':'accept or rework', 'type':'juridical'}
        await manager.send_direct_message(request.to_user,json.dumps(message))
    return response



@router.get('/v1/get/mibs')
def get_mib(problems_case_id:int=None):
    with SessionManager() as db_session:
        response = mib_attach_files.get_mib(problems_case_id, db_session)
    return response



@router.get('/v1/get/mib-types')
def get_mib_types():
    with SessionManager() as db_session:
        response = mib_attach_files.get_mib_types(db_session)
    return response









@router.get('/v1/get/state-notifications')
def get_auction_types(loan_portfolio_id:int=None, main_responsible_id:int=None, second_responsible_id:int=None, user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        db_session.add(user)
        response = problems_state_notification.get_promblems_state_notifications(loan_portfolio_id, user.id, main_responsible_id, second_responsible_id, db_session)
    return response