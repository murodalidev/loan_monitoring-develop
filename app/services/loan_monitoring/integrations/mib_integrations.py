import requests

from app.common.commit import flush_object
from app.models.problems_case.problems_assets.problems_assets_notification_model import ProblemsStateNotification
from app.services.loan_monitoring.problems_case.state_chains import set_chain_state_for_bpi
from .http_client.integrations_interface import HttpIntegrationsInterface
from fastapi import HTTPException
import json, uuid
from ....config.logs_config import info_logger
from .soliq_integrations import requestToSoliq, soliq_integrations_auth
from ....common.dictionaries.integrations_services import SERVICES, SERVICES_API
from .logs import add_log
ERROR_CODE = 500




def information_debtors_pinfl(request, user_id, db_session):
    interface = HttpIntegrationsInterface()

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + soliq_integrations_auth()
    }

    body = {
        "transaction_id": int(str(uuid.uuid1().int)[-19:]),
        "sender_pinfl": request.sender_pinfl,
        "purpose": request.purpose,
        "type" : request.type,
        "consent": request.consent,
        "pin": request.pin_or_inn,
    }
    
    response = requestToSoliq("POST", interface.mib_debtors_pinfl, headers, {}, json.dumps(body))
    if response == 0:
        info_logger.error("Eror in bux_balance_first_form status_code= %s",ERROR_CODE)
        raise HTTPException(status_code=ERROR_CODE, detail='Сервис временно недоступен, попробуйте позже.')
    if 'message' in response:
        info_logger.error("Eror in bux_balance_first_form status_code = %s, message = %s",ERROR_CODE, response['message'])
        raise HTTPException(status_code=ERROR_CODE, detail=response['message'])
    add_log(request.loan_portfolio_id, SERVICES.MIB.value, SERVICES_API.MIB_DEBTORS_PINFRL.value, user_id, interface.mib_debtors_pinfl, json.dumps(body), response, db_session)
    return response


def information_debtors_stir(request, user_id, db_session):
    interface = HttpIntegrationsInterface()

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + soliq_integrations_auth()
    }
    
    body = {
        "transaction_id": int(str(uuid.uuid1().int)[-19:]),
        "sender_pinfl": request.sender_pinfl,
        "purpose": request.purpose,
        "consent": request.consent,
        "inn": request.pin_or_inn,
    }
    
    response = requestToSoliq("POST", interface.mib_debtors_stir, headers, {}, json.dumps(body))
    if response == 0:
        info_logger.error("Eror in bux_balance_first_form status_code= %s",ERROR_CODE)
        raise HTTPException(status_code=ERROR_CODE, detail='Сервис временно недоступен, попробуйте позже.')
    if 'message' in response:
        info_logger.error("Eror in bux_balance_first_form status_code = %s, message = %s",ERROR_CODE, response['message'])
        raise HTTPException(status_code=ERROR_CODE, detail=response['message'])

    add_log(request.loan_portfolio_id, SERVICES.MIB.value, SERVICES_API.MIB_DEBTORS_STIR.value, user_id, interface.mib_debtors_stir, json.dumps(body), response, db_session)
    return response


def information_actions_pinfl(request, user_id, db_session):
    interface = HttpIntegrationsInterface()

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + soliq_integrations_auth()
    }

    body = {
        "transaction_id": str(uuid.uuid1().int)[-19:],
        "sender_pinfl": request.sender_pinfl,
        "purpose": request.purpose,
        "type" : request.type,
        "consent": request.consent,
        "pin": request.pin_or_inn,
        "work_number": request.work_number
    }

    response = requestToSoliq("POST", interface.mib_actions_pinfl, headers, {}, json.dumps(body))
    if response == 0:
        info_logger.error("Eror in bux_balance_first_form status_code= %s",ERROR_CODE)
        raise HTTPException(status_code=ERROR_CODE, detail='Сервис временно недоступен, попробуйте позже.')
    if 'message' in response:
        info_logger.error("Eror in bux_balance_first_form status_code = %s, message = %s",ERROR_CODE, response['message'])
        raise HTTPException(status_code=ERROR_CODE, detail=response['message'])

    add_log(request.loan_portfolio_id, SERVICES.MIB.value, SERVICES_API.MIB_ACTIONS_PINFRL.value, user_id, interface.mib_actions_pinfl, json.dumps(body), response, db_session)
    
    get_problems_state_notification = db_session.query(ProblemsStateNotification).filter(ProblemsStateNotification.loan_portfolio_id == request.loan_portfolio_id).first()
    if get_problems_state_notification is None:
        new_problems_state_notification = ProblemsStateNotification(loan_portfolio_id = request.loan_portfolio_id, bpi_status = True)
        db_session.add(new_problems_state_notification)
        flush_object(db_session)
    else:
        get_problems_state_notification.bpi_status = True
    
    set_chain_state_for_bpi(request.loan_id, db_session)
    return response


def information_actions_stir(request, user_id, db_session):
    interface = HttpIntegrationsInterface()

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + soliq_integrations_auth()
    }

    body = {
        "transaction_id": str(uuid.uuid1().int)[-19:],
        "sender_pinfl": request.sender_pinfl,
        "purpose": request.purpose,
        "type": request.type,
        "consent": request.consent,
        "inn": request.pin_or_inn,
        "work_number": request.work_number
    }

    response = requestToSoliq("POST", interface.mib_actions_stir, headers, {}, json.dumps(body))
    if response == 0:
        info_logger.error("Eror in bux_balance_first_form status_code= %s",ERROR_CODE)
        raise HTTPException(status_code=ERROR_CODE, detail='Сервис временно недоступен, попробуйте позже.')
    if 'message' in response:
        info_logger.error("Eror in bux_balance_first_form status_code = %s, message = %s",ERROR_CODE, response['message'])
        raise HTTPException(status_code=ERROR_CODE, detail=response['message'])

    add_log(request.loan_portfolio_id, SERVICES.MIB.value, SERVICES_API.MIB_ACTIONS_STIR.value, user_id, interface.mib_actions_stir, json.dumps(body), response, db_session)
    set_chain_state_for_bpi(request.loan_id, db_session)
    return response