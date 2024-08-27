import datetime, requests, logging, json, uuid
from app.config.config import ADLIYA_API
from fastapi import HTTPException
from .check_family_service import adliya_auth
from ...common.dictionaries.integrations_services import SERVICES, SERVICES_API
from ..loan_monitoring.integrations.logs import add_log
logger = logging.getLogger(__name__)


def notarial_ban(request, user_id, db_session):
    response = adliya_auth()
    if response == 0:
        raise HTTPException(status_code=500, detail='Сервис временно недоступен, попробуйте позже.')
    headers = {
            'Authorization': f'Bearer {response["token"]}',
            'Content-Type': 'application/json'
            }
    data = json.dumps({
        "jsonrpc": "2.0",
        "id": str(uuid.uuid1().int>>64)[:9],
        "method": "adliya.get_notarial_ban_by_reg_num",
        "params": {
            "reg_num": request.reg_num,
            "request_id": str(uuid.uuid1().int>>64)[:9],
            "request_date": str(datetime.datetime.now().date()),
            "declarant": {
                "company_inn": request.declarant.company_inn or request.declarant.company_inn or None,
                "mfo": request.declarant.mfo or request.declarant.mfo or None,
                "company_name": request.declarant.company_name or request.declarant.company_name or None,
                "representative_inn": request.declarant.representative_inn or request.declarant.representative_inn or None,
                "representative_fio": request.declarant.representative_fio or request.declarant.representative_fio or None,
            },
            "member": {
                "type": request.member.member_type and request.member.member_type or None,
                "inn": request.member.inn and request.member.inn or None,
                "pin": request.member.member_pinfl and request.member.member_pinfl or None,
                "pass_serial": request.member.pass_serial or request.member.pass_serial or None,
                "pass_num": request.member.pass_num or request.member.pass_num or None
            },
            "subject": {
                "type": request.subject.subject_type and request.subject.subject_type or None,
                "cadastre_num": request.subject.cadastre_num and request.subject.cadastre_num or None,
                "state_num": request.subject.state_num and request.subject.state_num or None,
                "engine_num": request.subject.engine_num and request.subject.engine_num or None,
                "body_num": request.subject.body_num and request.subject.body_num or None,
                "chassis_num": request.subject.chassis_num and request.subject.chassis_num or None,
            }
        }
        })
    try:
        r = requests.post(f'{ADLIYA_API}/api/v1/adliya/notarial-ban', 
                    headers = headers,
                    data=data,
                    timeout=(6, 30),
                    verify=False)
        res = r.json()
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=500, detail="Сервер билан вақтинчалик алоқа йўқ! Илтимос бир оздан сўнг қайта уриниб кўринг!")
    
    
    logger.info("notarial ban request has been established!")
    add_log(request.loan_portfolio_id, SERVICES.ADLIYA.value, SERVICES_API.ADLIYA_NOTARIAL_BAN.value, user_id, f'{ADLIYA_API}/api/v1/adliya/notarial-ban', json.dumps(data), res, db_session)
    return res




def notarial_ban_by_subject(request, user_id, db_session):
    response = adliya_auth()
    headers = {
            'Authorization': f'Bearer {response["token"]}',
            'Content-Type': 'application/json'
            }
    data = json.dumps({
        "jsonrpc": "2.0",
        "id": str(uuid.uuid1().int>>64)[:9],
        "method": "adliya.get_notarial_ban_by_subject",
        "params": {
            "type": request.subject_type,
            "cadastre_num": request.cadastre_num and request.cadastre_num or None,
            "state_num": request.state_num and request.state_num or None,
            "body_num": request.body_num and request.body_num or None,
            "engine_num": request.engine_num and request.engine_num or None,
            "chassis_num": request.chassis_num and request.chassis_num or None,
            "vehicle_id": request.vehicle_id and request.vehicle_id or None,
            }
        
        })
    try:
        r = requests.post(f'{ADLIYA_API}/api/v1/adliya/notarial-ban-subject', 
                    headers = headers,
                    data=data,
                    timeout=(6, 30),
                    verify=False)
        res = r.json()
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=500, detail="Сервер билан вақтинчалик алоқа йоқ! Илтимос бир оздан сўнг қайта уриниб кўринг!")
    
    
    logger.info("notarial ban by subject request has been established!")
    add_log(request.loan_portfolio_id, SERVICES.ADLIYA.value, SERVICES_API.ADLIYA_NOTARIAL_BAN_BY_SUBJECT.value, user_id, f'{ADLIYA_API}/api/v1/adliya/notarial-ban', json.dumps(data), res, db_session)
    return res