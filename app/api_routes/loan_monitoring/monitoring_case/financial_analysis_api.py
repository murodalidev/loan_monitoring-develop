from fastapi import APIRouter, Depends
from app.db.connect_db import SessionManager
from ....services.loan_monitoring.monitoring_case import financial_analysis_crud
from app.middleware.auth_file import AuthHandler
from ....schemas.monitoring_case_schemas import CreateFinAnalysis
from ....common import common_handler
auth_handler = AuthHandler()


router = APIRouter(
    prefix = "/monitoring-case/financial-analysis", tags=["Monitoring Case"]
)

#, user=Depends(auth_handler.auth_wrapper)
@router.post('/v1/create')
def portrfolio(request:CreateFinAnalysis):
    with SessionManager() as db_session:
        response = common_handler.handle_error(financial_analysis_crud.create_financial_analyse, request, db_session)
    return response

@router.get('/v1/get/all')
def portrfolio(monitoring_case_id:int):
    with SessionManager() as db_session:
        response = common_handler.handle_error(financial_analysis_crud.get_financial_analysis, monitoring_case_id, db_session)
    return response


@router.get('/v1/get/statuses')
def portrfolio():
    with SessionManager() as db_session:
        response = common_handler.handle_error(financial_analysis_crud.get_final_status, db_session)
    return response


@router.put('/v1/update{id}')
def portrfolio(id:int,request:CreateFinAnalysis):
    with SessionManager() as db_session:
        response = common_handler.handle_error(financial_analysis_crud.update_financial_analyse, id,request, db_session)
    return response






# @router.get('/v1/get/detail')
# def portrfolio(user_id:int, id):
#     with SessionManager() as db_session:
#         response = monitoring_case_crud.get_monitoring_detail(id,user_id,db_session)
#     return response