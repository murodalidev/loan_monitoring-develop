from fastapi import APIRouter
from ....services.loan_monitoring.monitoring_case import target_monitoring_crud
from ....services.loan_monitoring.task_manager import task_manager_crud
from ....services.loan_monitoring.monitoring_case import scheduled_monitoring_crud
from ....services.loan_monitoring.problems_case import problems_case_crud
from ....services.loan_monitoring.monitoring_case import target_monitoring_expiration
from app.db.connect_db import SessionManager
import json
from fastapi import BackgroundTasks
from ....services.loan_monitoring.loan_case import loan_case_crud
from ....schemas.monitoring_case_schemas import MonitoringCaseAppoint, TargetMonitoringAppoint, ScheduledMonitoringAppoint, LoanCaseChangeResponsible
from ....services.websocket.create_websocket import manager
from ....schemas.problems_case_schemas import ProblemsCaseSend
router = APIRouter(
    prefix = "/loan-case/monitoring", tags=["Loan Case"]
)



@router.post('/v1/appoint-responsible')
async def portrfolio(request:MonitoringCaseAppoint):
    with SessionManager() as db_session:
        response = loan_case_crud.appoint_responsible(request,db_session)
        message = {'notification_message':'appoint responsible', 'type':'loan'}
        await manager.send_direct_message(request.second_responsible_id,json.dumps(message))
    return response

@router.post('/v2/appoint-responsible')
async def portrfolio(request:MonitoringCaseAppoint):
    with SessionManager() as db_session:
        response = loan_case_crud.appoint_responsiblev2(request,db_session)
        message = {'notification_message':'appoint responsible', 'type':'loan'}
        await manager.send_direct_message(request.second_responsible_id,json.dumps(message))
    return response

@router.post('/v1/change-responsible')
async def cgange_responsible(request:LoanCaseChangeResponsible):
    with SessionManager() as db_session:
        response = loan_case_crud.update_responsible(request,db_session)
        message = {'notification_message':'change responsible', 'type':'loan'}
        await manager.send_direct_message(request.second_responsible_id,json.dumps(message))
    return response


@router.post('/v1/appoint-target-monitoring')
async def portrfolio(request:TargetMonitoringAppoint):
    with SessionManager() as db_session:
        response = target_monitoring_crud.appoint_target_monitoring(request,db_session)
        message = {'notification_message':'appoint target monitoring', 'type':'target'}
        await manager.send_direct_message(request.second_responsible_id,json.dumps(message))
    return response



@router.post('/v2/appoint-target-monitoring')
async def portrfolio(request:TargetMonitoringAppoint):
    with SessionManager() as db_session:
        response = target_monitoring_crud.appoint_target_monitoringv2(request,db_session)
        message = {'notification_message':'appoint target monitoring', 'type':'target'}
        await manager.send_direct_message(request.second_responsible_id,json.dumps(message))
    return response


@router.post('/v1/appoint-scheduled-monitoring')
async def portrfolio(request:ScheduledMonitoringAppoint):
    with SessionManager() as db_session:
        response = scheduled_monitoring_crud.appoint_scheduled_monitoring(request,db_session)
        message = {'notification_message':'appoint scheduled monitoring', 'type':'schedule'}
        await manager.send_direct_message(request.second_responsible_id,json.dumps(message))
    return response


@router.post('/v2/appoint-scheduled-monitoring')
async def portrfolio(request:ScheduledMonitoringAppoint):
    with SessionManager() as db_session:
        response = scheduled_monitoring_crud.appoint_scheduled_monitoringv2(request,db_session)
        message = {'notification_message':'appoint scheduled monitoring', 'type':'schedule'}
        await manager.send_direct_message(request.second_responsible_id,json.dumps(message))
    return response


@router.post('/v1/send-to-problems')
async def portrfolio(request:ProblemsCaseSend):
    with SessionManager() as db_session:
        response = problems_case_crud.send_to_problems(request,db_session)
        message = {'notification_message':'send to juridical', 'type':'juridical'}
        await manager.local_broadcast(response,json.dumps(message))
        
    return 'OK'



@router.get('/v1/get-expiration-to-user')
def get_expirations(user_id:int=None):
    with SessionManager() as db_session:
        response = target_monitoring_expiration.get_target_expirations_for_user(user_id, db_session)
    return response

@router.get('/v1/set-expiration')
def set_loan_expirations(back_task: BackgroundTasks):
    with SessionManager() as db_session:
        back_task.add_task(target_monitoring_expiration.set_monitoring_expired, db_session)
    return "OK"

@router.get('/v1/get-loan-task-statuses')
def get_loan_statuses():
    with SessionManager() as db_session:
        response = task_manager_crud.get_task_status(db_session)
    return response

# @router.get('/v1/get-expiration-to-user_detail')
# def get_expirations_detail(user_id:int=None):
#     with SessionManager() as db_session:
#         response = target_monitoring_expiration.get_target_expirations_for_user_detail(user_id, db_session)
#     return response


@router.get('/v1/get-target-expiration-to-user_detail')
def get_target_expirations_detail(page:int, size:int, user_id:int=None, month:int=None):
    with SessionManager() as db_session:
        response = target_monitoring_expiration.get_target_expirations_for_user_detail(page, size, user_id, month, db_session)
    return response

@router.get('/v1/get-scheduled-expiration-to-user_detail')
def get_scheduled_expirations_detail(page:int, size:int, user_id:int=None, month:int=None):
    with SessionManager() as db_session:
        response = target_monitoring_expiration.get_scheduled_expirations_for_user_detail(page, size, user_id, month, db_session)
    return response

@router.get('/v1/get-unscheduled-expiration-to-user_detail')
def get_unscheduled_expirations_detail(page:int, size:int, user_id:int=None, month:int=None):
    with SessionManager() as db_session:
        response = target_monitoring_expiration.get_unscheduled_expirations_for_user_detail(page, size, user_id, month, db_session)
    return response
    


@router.get('/v1/get-all-expiration-to-user_detail')
def get_all_expirations_detail(page:int, size:int, user_id:int=None, month:int=None):
    with SessionManager() as db_session:
        response = target_monitoring_expiration.get_all_expirations_for_user_detail(page, size, user_id, month, db_session)
    return response