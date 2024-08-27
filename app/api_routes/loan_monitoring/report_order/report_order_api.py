from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from app.db.connect_db import SessionManager
from app.middleware.auth_file import AuthHandler
from ....services.reports import report_to_excel_service, business_kad_report, adliya_report
from ....schemas.monitoring_case_schemas import  ExcelReportPeriod
from app.services.loan_monitoring.report_order import report_order_crud
auth_handler = AuthHandler()


router = APIRouter(
    prefix = "/report-order", tags=["Report Order"]
)


@router.post('/v1/order')
def oreder_report(request:ExcelReportPeriod,back_task: BackgroundTasks, user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        db_session.add(user)
        report_order_crud.check_if_report_exists(user.id,request.report_type, request.report_by, db_session)
        back_task.add_task(report_to_excel_service.create_report_to_excel, request, user.id, db_session)
        #report_to_excel_service.create_report_to_excel(request, user.id, db_session)
    return 'Отчет появится через некоторое время'


@router.post('/v1/order-kad-business')
def oreder_report(request:ExcelReportPeriod,back_task: BackgroundTasks, user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        db_session.add(user)
        report_order_crud.check_if_report_exists(user.id,request.report_type, request.report_by, db_session)
        back_task.add_task(business_kad_report.create_report_to_excel, request, user.id, db_session)
    return 'Отчет появится через некоторое время'



@router.post('/v1/order-adliya')
def oreder_report(request:ExcelReportPeriod,back_task: BackgroundTasks, user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        db_session.add(user)
        report_order_crud.check_if_report_exists(user.id,request.report_type, 1, db_session)
        back_task.add_task(adliya_report.create_adliya_report_to_excel, request, user.id, db_session)
    return 'Отчет появится через некоторое время'




@router.get('/v1/get-all')
def oreder_report(report_type:int, user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        db_session.add(user)
        result = report_order_crud.get_report_for_user(user.id, report_type, db_session)
    return result

@router.get('/v1/get-report-by')
def oreder_report():
    with SessionManager() as db_session:
        result = report_order_crud.get_report_by(db_session)
    return result

@router.delete('/v1/delete')
def delete_report(report_id:int, user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        db_session.add(user)
        result = report_order_crud.delete_report_for_user(report_id, db_session)
    return result