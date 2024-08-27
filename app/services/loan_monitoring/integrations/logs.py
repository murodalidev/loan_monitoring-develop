import requests
from datetime import datetime
from ....models.integrations.integrations_log import Integrations_log
from ....models.integrations.integrations_service_api import Integrations_service_api
from fastapi import HTTPException
import uuid
from ....config.logs_config import info_logger
from ....common.commit import commit_object, flush_object
from ....common.dictionaries.integrations_services import SERVICES



def add_log(loan_portfolio_id, service_id, service_api_id, user_id, api, request, response, db_session):
    new_log = Integrations_log(loan_portfolio_id=loan_portfolio_id, service_id=service_id, service_api_id=service_api_id, user_id=user_id, api=api, request=request, response=response, created_at=datetime.now())
    db_session.add(new_log)
    commit_object(db_session)
    return "OK"


def get_log(size, page, service_api_id, loan_portfolio_id, db_session):
    get_history = db_session.query(Integrations_log)
    if loan_portfolio_id is not None:
        get_history = get_history.filter(Integrations_log.loan_portfolio_id == loan_portfolio_id)
    get_history = get_history.filter(Integrations_log.service_api_id == service_api_id).order_by(Integrations_log.created_at.desc())
    
    count = get_history.count()
    get_history = get_history.limit(size).offset((page-1)*size).all()
    logs = []
    for history in get_history:
        logs.append({"loan_portfolio_id": history.loan_portfolio_id,
                     "service_id": history.service_id,
                     "service_api_id": history.service_api_id,
                     "request": history.request,
                     "response": history.response,
                     "user":{"full_name": history.user.full_name,
                             "department": history.user.depart.name,
                             "position": history.user.pos.name},
                     "created_at":history.created_at})
    return {"items": logs,
            "total":count,
            "page":page,
            "size":size}


def get_service_api_list(db_session):
    return db_session.query(Integrations_service_api).all()