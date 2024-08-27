import requests
from .http_client.integrations_interface import HttpIntegrationsInterface
from fastapi import HTTPException
import json, uuid
from datetime import date
from ....config.logs_config import info_logger
from ....common.dictionaries.integrations_services import SERVICES, SERVICES_API
from .logs import add_log
ERROR_CODE = 500


def requestToAdliya(method, url, headers, params, data):
    try:
        response = requests.request(method, url, headers=headers, data=data)
    except Exception as e:
        info_logger.error(str(e))
        return 0
    print(response)
    #raise {'code':request.status_code, 'message': 'Unable to connect to server api'}
    return response.json() 

def adliya_integrations_auth():
    interface = HttpIntegrationsInterface()

    headers = {
        'Content-Type': 'application/json'
    }
    response = requestToAdliya("POST", interface.adliya_auth, headers,  {}, interface.get_adliya_token_data())
    
    if response == 0:
        info_logger.error("adliya_integrations_auth FAILED")
        return 'Сервис временно недоступен, попробуйте позже.'
    
    elif 'token' in response:
        return response['token']
    
    return ''




def adliya_lifting_ban_imposed_by_bank(request, user_id, db_session):

    interface = HttpIntegrationsInterface()

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + adliya_integrations_auth()
    }

    body = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid1().int>>64)[:9],
        "method": "adliya.remove_notarial_ban_set_by_bank",
    }
    params = {
        "request_id": str(uuid.uuid1().int>>64)[:9],
        "reg_num": request.reg_num,
        "statement": {
            "doc_type": request.doc_type,
            "doc_num": request.doc_num,
            "doc_date": request.doc_date,
            "org_type": request.org_type,
            "org_name": request.org_name,
            "org_post": request.org_post,
            "org_fio": request.org_fio,
            "base_document": request.base_document
        }
    }

    declarant = {
            "company_inn": request.company_inn,
            "company_name": request.company_name,
            "representative_fio": request.company_name
        }
    if request.mfo:
        declarant.update({"mfo": request.mfo})
    if request.representative_inn:
        declarant.update({"representative_inn": request.representative_inn})

    params.update({"declarant":declarant})
    body.update({"params":params})
    response = requestToAdliya("POST", interface.adliya_lifting_ban_imposed_by_bank, headers, {}, json.dumps(body))
    if response == 0:
        info_logger.error("Eror in adliya_lifting_ban_imposed_by_bank status_code= %s",ERROR_CODE)
        raise HTTPException(status_code=ERROR_CODE, detail='Сервис временно недоступен, попробуйте позже.')
    if 'message' in response:
        info_logger.error("Eror in adliya_lifting_ban_imposed_by_bank status_code = %s, message = %s",ERROR_CODE, response['message'])
        raise HTTPException(status_code=ERROR_CODE, detail=response['message'])
    
    add_log(request.loan_portfolio_id, SERVICES.ADLIYA.value, SERVICES_API.ADLIYA_LIFTING_BAN_BANK.value, user_id, interface.adliya_lifting_ban_imposed_by_bank, json.dumps(body), response, db_session)
    return response




def adliya_lifting_ban_imposed_by_notary(request, user_id, db_session):

    interface = HttpIntegrationsInterface()

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + adliya_integrations_auth()
    }

    body = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid1().int>>64)[:9],
        "method": "adliya.remove_notarial_ban_set_by_notary",
    }
    params = {
        "request_id": str(uuid.uuid1().int>>64)[:9],
        "reg_num": request.reg_num,
        "statement": {
            "doc_type": request.doc_type,
            "doc_num": request.doc_num,
            "doc_date": request.doc_date,
            "org_type": request.org_type,
            "org_name": request.org_name,
            "org_post": request.org_post,
            "org_fio": request.org_fio,
            "base_document": request.base_document
        }
    }

    declarant = {
            "company_inn": request.company_inn
        }
    if request.company_name:
        declarant.update({"company_name": request.company_name})
    if request.representative_fio:
        declarant.update({"representative_fio": request.representative_fio})
    if request.mfo:
        declarant.update({"mfo": request.mfo})
    if request.representative_inn:
        declarant.update({"representative_inn": request.representative_inn})

    params.update({"declarant":declarant})
    body.update({"params":params})
    response = requestToAdliya("POST", interface.adliya_lifting_ban_imposed_by_notary, headers, {}, json.dumps(body))
    if response == 0:
        info_logger.error("Eror in adliya_lifting_ban_imposed_by_notary status_code= %s",ERROR_CODE)
        raise HTTPException(status_code=ERROR_CODE, detail='Сервис временно недоступен, попробуйте позже.')
    if 'message' in response:
        info_logger.error("Eror in adliya_lifting_ban_imposed_by_notary status_code = %s, message = %s",ERROR_CODE, response['message'])
        raise HTTPException(status_code=ERROR_CODE, detail=response['message'])
    
    add_log(request.loan_portfolio_id, SERVICES.ADLIYA.value, SERVICES_API.ADLIYA_LIFTING_BAN_NOTARY.value, user_id, interface.adliya_lifting_ban_imposed_by_notary, json.dumps(body), response, db_session)
    return response


def adliya_personal_document_type(user_id, db_session):

    interface = HttpIntegrationsInterface()

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + adliya_integrations_auth()
    }
    
    body = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid1().int>>64)[:9],
        "method": "adliya.get_notary_ref_personal_document_type",
    }
    
    response = requestToAdliya("POST", interface.adliya_personal_document_type, headers, {}, json.dumps(body))
    if response == 0:
        info_logger.error("Eror in adliya_personal_document_type status_code= %s",ERROR_CODE)
        raise HTTPException(status_code=ERROR_CODE, detail='Сервис временно недоступен, попробуйте позже.')
    if 'message' in response:
        info_logger.error("Eror in adliya_personal_document_type status_code = %s, message = %s",ERROR_CODE, response['message'])
        raise HTTPException(status_code=ERROR_CODE, detail=response['message'])
    
    # add_log(SERVICES.ADLIYA.value, SERVICES_API.ADLIYA_PERSONAL_DOCUMENT_TYPE.value, user_id, interface.adliya_personal_document_type, json.dumps(body), response, db_session)
    return response


def adliya_org_type(user_id, db_session):

    interface = HttpIntegrationsInterface()

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + adliya_integrations_auth()
    }
    
    body = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid1().int>>64)[:9],
        "method": "adliya.get_notary_ref_org_type",
    }
    
    response = requestToAdliya("POST", interface.adliya_org_type, headers, {}, json.dumps(body))
    if response == 0:
        info_logger.error("Eror in adliya_org_type status_code= %s",ERROR_CODE)
        raise HTTPException(status_code=ERROR_CODE, detail='Сервис временно недоступен, попробуйте позже.')
    if 'message' in response:
        info_logger.error("Eror in adliya_org_type status_code = %s, message = %s",ERROR_CODE, response['message'])
        raise HTTPException(status_code=ERROR_CODE, detail=response['message'])
    
    # add_log(SERVICES.ADLIYA.value, SERVICES_API.ADLIYA_ORG_TYPE.value, user_id, interface.adliya_org_type, json.dumps(body), response, db_session)
    return response


def adliya_subject_type(user_id, db_session):

    interface = HttpIntegrationsInterface()

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + adliya_integrations_auth()
    }
    
    body = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid1().int>>64)[:9],
        "method": "adliya.get_notary_ref_subject_type",
    }
    
    response = requestToAdliya("POST", interface.adliya_subject_type, headers, {}, json.dumps(body))
    if response == 0:
        info_logger.error("Eror in adliya_subject_type status_code= %s",ERROR_CODE)
        raise HTTPException(status_code=ERROR_CODE, detail='Сервис временно недоступен, попробуйте позже.')
    if 'message' in response:
        info_logger.error("Eror in adliya_subject_type status_code = %s, message = %s",ERROR_CODE, response['message'])
        raise HTTPException(status_code=ERROR_CODE, detail=response['message'])
    
    # add_log(SERVICES.ADLIYA.value, SERVICES_API.ADLIYA_SUBJECT_TYPE.value, user_id, interface.adliya_subject_type, json.dumps(body), response, db_session)
    return response


def adliya_doc_type(user_id, db_session):

    interface = HttpIntegrationsInterface()

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + adliya_integrations_auth()
    }
    
    body = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid1().int>>64)[:9],
        "method": "adliya.get_notary_ref_doc_type",
    }
    
    response = requestToAdliya("POST", interface.adliya_doc_type, headers, {}, json.dumps(body))
    if response == 0:
        info_logger.error("Eror in adliya_doc_type status_code= %s",ERROR_CODE)
        raise HTTPException(status_code=ERROR_CODE, detail='Сервис временно недоступен, попробуйте позже.')
    if 'message' in response:
        info_logger.error("Eror in adliya_doc_type status_code = %s, message = %s",ERROR_CODE, response['message'])
        raise HTTPException(status_code=ERROR_CODE, detail=response['message'])
    
    # add_log(SERVICES.ADLIYA.value, SERVICES_API.ADLIYA_DOC_TYPE.value, user_id, interface.adliya_doc_type, json.dumps(body), response, db_session)
    return response


def adliya_post_info(user_id, db_session):

    interface = HttpIntegrationsInterface()

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + adliya_integrations_auth()
    }
    
    body = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid1().int>>64)[:9],
        "method": "adliya.get_notary_ref_org_post",
    }
    
    response = requestToAdliya("POST", interface.adliya_post_info, headers, {}, json.dumps(body))
    if response == 0:
        info_logger.error("Eror in adliya_post_info status_code= %s",ERROR_CODE)
        raise HTTPException(status_code=ERROR_CODE, detail='Сервис временно недоступен, попробуйте позже.')
    if 'message' in response:
        info_logger.error("Eror in adliya_post_info status_code = %s, message = %s",ERROR_CODE, response['message'])
        raise HTTPException(status_code=ERROR_CODE, detail=response['message'])
    
    # add_log(SERVICES.ADLIYA.value, SERVICES_API.ADLIYA_POST_INFO.value, user_id, interface.adliya_post_info, json.dumps(body), response, db_session)
    return response