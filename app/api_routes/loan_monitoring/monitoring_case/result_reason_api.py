from fastapi import APIRouter, Depends
from app.services.loan_monitoring.monitoring_case import non_target_reasons
from app.db.connect_db import SessionManager
from app.schemas.result_reason_schemas import ResultReasonSchema
from app.middleware.auth_file import AuthHandler


auth_handler = AuthHandler()
router = APIRouter(
    prefix = "/result-reason", tags=["Monitoring Case"]
)


@router.get('/v1/read/all')
def reason_page():
    with SessionManager() as db_session:
        reasons = non_target_reasons.get_all_reasons(db_session)
    return {"reasons":reasons}


@router.post('/v1/create')
def reason_add(request: ResultReasonSchema):
    with SessionManager() as db_session:
        status = non_target_reasons.create_reason(request, db_session)
    return status



@router.put('/v1/update/{id}')
def reason_update(id:int, request: ResultReasonSchema):
    with SessionManager() as db_session:
        status = non_target_reasons.update_reason(id, request, db_session)
    return status


@router.delete('/v1/delete/{id}')
def reason_delete(id:int):
    with SessionManager() as db_session:
        status = non_target_reasons.delete_reason(id, db_session)
    return status