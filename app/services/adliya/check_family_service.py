import requests
import logging
from app.config.config import ADLIYA_API, ADLIYA_LOGIN, ADLIYA_PASSWORD
from fastapi import HTTPException
import json
import uuid
from ...config.logs_config import info_logger
from ...common.dictionaries.integrations_services import SERVICES, SERVICES_API
from ..loan_monitoring.integrations.logs import add_log

adliya_api =ADLIYA_API
auth_api= ADLIYA_API + '/api/v1/adliya/auth/authenticate'
check_family_api=ADLIYA_API + '/api/v1/adliya/check-family'




def check_family(request, user_id, db_session):
    response = adliya_auth()
    
    if response == 0:
        raise HTTPException(status_code=500, detail='Сервис временно недоступен, попробуйте позже.')
    headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {response['token']}"
            }
    data = {
    "jsonrpc":"2.0",
     "id":uuid.uuid1().int>>64,
      "method":"zags.check_family_ties_by_pins",
       "params":{
           "base_pin" : request.base_pinfl,
           "to_check" : request.list_check_pinfl
       }
}
    try:
        r = requests.post(f'{ADLIYA_API}/api/v1/adliya/check-family', 
                    headers = headers,
                    data=json.dumps(data),
                    timeout=(6, 30),
                    verify=False)
        res = r.json()
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=500, detail="Сервер билан вақтинчалик алоқа йоқ! Илтимос бир оздан сўнг қайта уриниб кўринг!")
    
    
    add_log(request.loan_portfolio_id, SERVICES.ADLIYA.value, SERVICES_API.ADLIYA_CHECK_FAMILY.value, user_id, check_family_api, json.dumps(data), res, db_session)
    return res



def adliya_auth():
    data = json.dumps({
         "username" : ADLIYA_LOGIN,
         "password" : ADLIYA_PASSWORD
       })
    headers = {
            'Content-Type': 'application/json'
            }
    
    try:
        request = requests.request("POST", auth_api, headers=headers, data=data)
        response = request.json()
    except Exception as e:
        info_logger.error(str(e))
        return 0
    return response 