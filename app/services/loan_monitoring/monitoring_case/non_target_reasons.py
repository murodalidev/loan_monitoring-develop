from app.models.monitoring_case.reslut_reason_model import ResultReason
from ....common.is_empty import is_empty, is_exists
from ....common.commit import commit_object


def create_reason(request, db_session):
    get_reason = db_session.query(ResultReason).filter(ResultReason.name == request.reason_name).first()
    is_empty(get_reason, 400, 'monitoring result reason has already created!')
    new_reason = ResultReason(name=request.reason_name, code=request.code)
    db_session.add(new_reason)
    commit_object(db_session)
    return {"result":"OK"}



def get_all_reasons(db_session):
    get_reasons = db_session.query(ResultReason).all()
    reasons = []
    reason_other = None
    for reason in get_reasons:
        if reason.code==11:
            reason_other = reason
        else:
            reasons.append({"id":reason.id,
                "reason_name":reason.name,
                "code":reason.code})
            
    reasons.append({"id":reason_other.id,
                "reason_name":reason_other.name,
                "code":reason_other.code})
    return reasons



def get_reason(reson_id, db_session):
    return db_session.query(ResultReason).filter(ResultReason.id == reson_id).first()



def update_reason(id, request, db_session):
    get_reason = db_session.query(ResultReason).filter(ResultReason.name == request.reason_name).filter(ResultReason.id == id).first()
    is_empty(get_reason, 400, 'result reason name has already created!')
    get_reason = db_session.query(ResultReason).filter(ResultReason.id == id).first()
    get_reason.name=request.reason_name
    if request.code is not None:
        get_reason.code=request.code
    commit_object(db_session)
    return {"result":"OK"}



def delete_reason(id, db_session):
    get_reason = db_session.query(ResultReason).filter(ResultReason.id == id).first()
    is_exists(get_reason, 400, 'result reason not found')
    db_session.delete(get_reason)
    commit_object(db_session)
    return {"result":"OK"}
