from fastapi import APIRouter, Depends, UploadFile, Body
from typing import Union, List
from app.db.connect_db import SessionManager
from fastapi import BackgroundTasks
from ....services.loan_monitoring.loan_case import loan_case_crud
from ....services.loan_monitoring.general_tasks import general_tasks_crud
from ....schemas.monitoring_case_schemas import LoanCaseClose, ReplyToNewLoan, ExcelReportPeriod
from ....schemas.files_types_schemas import FileTypesToGeneralTasks
from app.middleware.auth_file import AuthHandler
from ....services.websocket.create_websocket import manager
import json
from ....common.save_file import save_file
from ....services.monitoring_files import files_crud
from ....services.reports import report_to_excel_service
from ....services.loan_monitoring.loan_case import cron_loan_case
from ....config.cache import cache_get, cache_add
auth_handler = AuthHandler()


router = APIRouter(
    prefix = "/loan-case", tags=["Loan Case"]
)



@router.get('/v1/get/details')
def portrfolio(id:int, user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        db_session.add(user)
        response = loan_case_crud.get_loan_case_details(id, db_session)
    return {"loan_case_details":response}


@router.get('/v1/get/history')
def portrfolio(loan_case_id:int, general_task_id:int):
    with SessionManager() as db_session:
        response = loan_case_crud.get_loan_case_history(loan_case_id,general_task_id, db_session)
    return response


@router.post('/v1/reply-to-new-loan')
async def portrfolio(request:ReplyToNewLoan= Body(...), files: List[UploadFile] = None):
    with SessionManager() as db_session:
        file_path = [save_file(file) for file in files]
        response = loan_case_crud.reply_to_new_juridical_case(request,file_path,db_session)
        message = {'notification_message':'reply to new loan', 'type':'juridical'}
        await manager.send_direct_message(response['to_user_id'],json.dumps(message))
    return 'OK'




@router.post('/v1/close')
def portrfolio(request:LoanCaseClose):
    with SessionManager() as db_session:
        response = loan_case_crud.close_loan_case(request, db_session)
    return response





@router.get('/v1/get/file')
def portrfolio(file_path:str):
    response = loan_case_crud.get_file(file_path)
    return response



@router.get('/v1/get/user-stats-for-kad')
def statistics_for_kad(user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        db_session.add(user)
        cache = cache_get(user.id, 'kad')
        if cache:
            return cache
        else:
            response = loan_case_crud.get_statistics_for_kad(user, db_session)
            if response['statistics_for_kad'] is not None:
                cache_add(user.id, 'kad', response)
            return response

@router.get('/v1/get/user-stats-for-problem')
def statistics_for_problem(user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        db_session.add(user)
        cache = cache_get(user.id, 'problem')
        if cache:
            return cache
        else:
            response = loan_case_crud.get_statistics_for_problem(user, db_session)
            if response['statistics_for_problems'] is not None:
                cache_add(user.id, 'problem', response)
            return response



@router.get('/v1/get/user-stats-for-business')
def statistics_for_business(user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        db_session.add(user)
        cache = cache_get(user.id, 'business')
        if cache:
            return cache
        else:
            response = loan_case_crud.get_statistics_for_business(user, db_session)
            if response['statistics_for_business'] is not None:
                cache_add(user.id, 'business', response)
            return response




@router.get('/v1/get/all-stats')
def portrfolio(user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        db_session.add(user)
        cache = cache_get(user.id, 'all')
        if cache:
            return cache
        else:
            response = loan_case_crud.get_all_stats(user, db_session)
            if response['all_statistics'] is not None:
                cache_add(user.id, 'all', response)
            return response

@router.get('/v1/get/files-by-param')
def portrfolio(juridical_case_id:str):
    with SessionManager() as db_session:
        categories = files_crud.get_files_by_param(juridical_case_id,db_session)
    return categories

@router.get('/v1/get/file-types')
def get_file_types():
    with SessionManager() as db_session:
        file_types = files_crud.get_file_types(db_session)
    return file_types

@router.post('/v1/attach-general-tasks-to-types')
def attach_general_tasks_to_ftype(request:FileTypesToGeneralTasks):
    with SessionManager() as db_session:
        status = files_crud.append_file_to_types(request, db_session)
    return status

@router.get('/v1/file-types-by-general-task')
def attach_general_tasks_to_ftype(general_task_id:int = None):
    with SessionManager() as db_session:
        status = files_crud.get_ftypes_by_general_task(general_task_id, db_session)
    return status




# @router.post('/v1/get/report-to-excel')
# # def report_to_excel(back_task: BackgroundTasks, period:ExcelReportPeriod):
# def report_to_excel(period:ExcelReportPeriod):
#     with SessionManager() as db_session:
#         status = report_to_excel_service.create_report_to_excel(period, db_session)
#         # categories = report_to_excel_service.create_report_to_excel(db_session)
#     return status
#     return "Отчет в процессе создания"




@router.get('/v1/get/general-tasks-for-filter')
def portrfolio(user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        db_session.add(user)
        general_tasks = general_tasks_crud.get_general_tasks_for_filter(user.department, db_session)
    return general_tasks




@router.get('/v1/send-to-problems')
def loan_send_to_problems():
    with SessionManager() as db_session:
        categories = cron_loan_case.loan_case_send_to_problems(db_session)
    return categories



@router.get('/v1/send-notification-about-dedline')
def send_notification_about_dedline(back_task: BackgroundTasks):
    with SessionManager() as db_session:
        back_task.add_task(cron_loan_case.notify_about_dedline, db_session)
    return 'OK'
