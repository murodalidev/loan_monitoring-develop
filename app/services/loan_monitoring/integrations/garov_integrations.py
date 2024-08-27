import requests
from .http_client.integrations_interface import HttpIntegrationsInterface
from fastapi import HTTPException
import json
from ....config.logs_config import info_logger
from ....common.dictionaries.integrations_services import SERVICES, SERVICES_API
from .logs import add_log
ERROR_CODE = 500


def requestToGarov(method, url, headers, params, data):
    try:
        
        response = requests.request(method, url, headers=headers, data=data)
        
    except Exception as e:
        info_logger.error(str(e))
        return 0
        #raise {'code':request.status_code, 'message': 'Unable to connect to server api'}
    return response.json() 

def garov_integrations_auth():
    interface = HttpIntegrationsInterface()
    headers = {
        'Content-Type': 'application/json'
    }
    response = requestToGarov("POST", interface.garov_auth, headers,  {}, interface.get_garov_token_data())
    if response == 0:
        info_logger.error("garov_integrations_auth FAILED")
        return 'Сервис временно недоступен, попробуйте позже.'
    
    elif 'token' in str(response):
        return response['token']
    
    return ''



def garov_notary_ban_list(request, user_id, db_session):
    interface = HttpIntegrationsInterface()

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + garov_integrations_auth()
    }

    body = {
            "member": {
                "type": request.member_type,
                "inn": request.inn and request.inn or None,
                "pin": request.pin and request.pin or None,
                "pass_serial": request.pass_serial and request.pass_serial or None,
                "pass_num": request.pass_num and request.pass_num or None
                },
            "subject": {
                "type": request.subject_type,
                "cadastre_num": request.cadastre_num and request.cadastre_num or None,
                "state_num": request.state_num and request.state_num or None,
                "engine_num": request.engine_num and request.engine_num or None,
                "body_num": request.body_num and request.body_num or None,
                "chassis_num": request.chassis_num and request.chassis_num or None,
                "vehicle_id": request.vehicle_id and request.vehicle_id or None
                }
            }

    response = requestToGarov("POST", interface.garov_notary_ban_list, headers, {}, json.dumps(body))
    if response == 0:
        info_logger.error("Eror in garov_notary_ban_list status_code= %s",ERROR_CODE)
        raise HTTPException(status_code=ERROR_CODE, detail='Сервис временно недоступен, попробуйте позже.')
    if 'message' in response:
        info_logger.error("Eror in garov_notary_ban_list status_code = %s, message = %s",ERROR_CODE, response['message'])
        raise HTTPException(status_code=ERROR_CODE, detail=response['message'])
    
    add_log(request.loan_portfolio_id, SERVICES.GAROV.value, SERVICES_API.GAROV_NOTARY_BAN_LIST.value, user_id, interface.garov_notary_ban_list, json.dumps(body), response, db_session)
    return response



def garov_notary_ban(request, user_id, db_session):
    interface = HttpIntegrationsInterface()

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + garov_integrations_auth()
    }

    body = {
            "code": request.code and request.code or None,
            "doc_num": request.doc_num and request.doc_num or None,
            "doc_date": request.doc_date and request.doc_date or None,
            "ban_edate": request.ban_edate and request.ban_edate or None,
            "debtor": {
                "subject_type": request.subject_type and request.subject_type or None,
                "country": request.country and request.country or None,
                "pass_type": request.pass_type and request.pass_type or None,
                "issue_org": request.issue_org and request.issue_org or None,
                "issue_date": request.issue_date and request.issue_date or None
                },
            "object": {
                "type": request.type and request.type or None,
                "cadaster_num": request.cadaster_num and request.cadaster_num or None,
                "district": request.district and request.district or None,
                "street": request.street and request.street or None,
                "home": request.home and request.home or None,
                "flat": request.flat and request.flat or None,
                "block": request.block and request.block or None,
                "obj_name": request.obj_name and request.obj_name or None,
                "state_num": request.state_num and request.state_num or None,
                "engine_num": request.engine_num and request.engine_num or None,
                "body_num": request.body_num and request.body_num or None,
                "chassis_num": request.chassis_num and request.chassis_num or None,
                "mark": request.mark and request.mark or None,
                "year_create": request.year_create and request.year_create or None,
                "color": request.color and request.color or None,
                "tech_serial": request.tech_serial and request.tech_serial or None,
                "tech_num": request.tech_num and request.tech_num or None,
                "tech_date": request.tech_date and request.tech_date or None,
                "tech_issue": request.tech_issue and request.tech_issue or None,
                "vehicle_id": request.vehicle_id and request.vehicle_id or None
                }
            }

    response = requestToGarov("POST", interface.garov_notary_ban, headers, {}, json.dumps(body))
    if response == 0:
        info_logger.error("Eror in garov_notary_ban status_code= %s",ERROR_CODE)
        raise HTTPException(status_code=ERROR_CODE, detail='Сервис временно недоступен, попробуйте позже.')
    if 'message' in response:
        info_logger.error("Eror in garov_notary_ban status_code = %s, message = %s",ERROR_CODE, response['message'])
        raise HTTPException(status_code=ERROR_CODE, detail=response['message'])
    
    add_log(request.loan_portfolio_id, SERVICES.GAROV.value, SERVICES_API.GAROV_NOTARY_BAN.value, user_id, interface.garov_notary_ban, json.dumps(body), response, db_session)
    return response


def garov_notary_ban_cancel(request, user_id, db_session):
    interface = HttpIntegrationsInterface()

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + garov_integrations_auth()
    }

    body = {
            "code": request.code,
            "ban_num": request.ban_num,
            "doc_type": request.doc_type,
            "doc_num": request.doc_num,
            "doc_date": request.doc_date
            }

    response = requestToGarov("POST", interface.garov_notary_ban_cancel, headers, {}, json.dumps(body))
    if response == 0:
        info_logger.error("Eror in garov_notary_ban_cancel status_code= %s",ERROR_CODE)
        raise HTTPException(status_code=ERROR_CODE, detail='Сервис временно недоступен, попробуйте позже.')
    if 'message' in response:
        info_logger.error("Eror in garov_notary_ban_cancel status_code = %s, message = %s",ERROR_CODE, response['message'])
        raise HTTPException(status_code=ERROR_CODE, detail=response['message'])
    
    add_log(request.loan_portfolio_id, SERVICES.GAROV.value, SERVICES_API.GAROV_NOTARY_BAN_CANCEL.value, user_id, interface.garov_notary_ban_cancel, json.dumps(body), response, db_session)
    return response


def get_notary_subject_type():
    interface = HttpIntegrationsInterface()

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + garov_integrations_auth()
    }

    response = requestToGarov("GET", interface.garov_get_notary_subject_type, headers, {}, {})
    if response == 0:
        info_logger.error("Eror in garov_get_notary_subject_type status_code= %s",ERROR_CODE)
        raise HTTPException(status_code=ERROR_CODE, detail='Сервис временно недоступен, попробуйте позже.')
    if 'message' in response:
        info_logger.error("Eror in garov_get_notary_subject_type status_code = %s, message = %s",ERROR_CODE, response['message'])
        raise HTTPException(status_code=ERROR_CODE, detail=response['message'])

    return response



def get_notary_property_type():
    interface = HttpIntegrationsInterface()

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + garov_integrations_auth()
    }

    response = requestToGarov("GET", interface.garov_get_notary_property_type, headers, {}, {})
    if response == 0:
        info_logger.error("Eror in garov_get_notary_property_type status_code= %s",ERROR_CODE)
        raise HTTPException(status_code=ERROR_CODE, detail='Сервис временно недоступен, попробуйте позже.')
    if 'message' in response:
        info_logger.error("Eror in garov_get_notary_property_type status_code = %s, message = %s",ERROR_CODE, response['message'])
        raise HTTPException(status_code=ERROR_CODE, detail=response['message'])

    return response



def get_notary_document_type():
    interface = HttpIntegrationsInterface()

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + garov_integrations_auth()
    }

    response = requestToGarov("GET", interface.garov_get_notary_document_type, headers, {}, {})
    if response == 0:
        info_logger.error("Eror in garov_get_notary_document_type status_code= %s",ERROR_CODE)
        raise HTTPException(status_code=ERROR_CODE, detail='Сервис временно недоступен, попробуйте позже.')
    if 'message' in response:
        info_logger.error("Eror in garov_get_notary_document_type status_code = %s, message = %s",ERROR_CODE, response['message'])
        raise HTTPException(status_code=ERROR_CODE, detail=response['message'])

    return response