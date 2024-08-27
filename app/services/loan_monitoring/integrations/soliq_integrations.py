import requests
from .http_client.integrations_interface import HttpIntegrationsInterface
from fastapi import HTTPException
import json
from ....config.logs_config import info_logger
from ....common.dictionaries.integrations_services import SERVICES, SERVICES_API
from .logs import add_log
ERROR_CODE = 500


def requestToSoliq(method, url, headers, params, data):
  try:
    
    response = requests.request(method, url, headers=headers, data=data)
    
  except Exception as e:
    
    info_logger.error(str(e))
    return 0
  if response.status_code == 204:
    detail= 'Нет данных'
    info_logger.error(detail)
    raise HTTPException(status_code=response.status_code, detail=detail)
    #raise {'code':request.status_code, 'message': 'Unable to connect to server api'}
  return response.json() 

def soliq_integrations_auth():
    interface = HttpIntegrationsInterface()
    headers = {
        'Content-Type': 'application/json'
    }
    response = requestToSoliq("POST", interface.soliq_auth, headers,  {}, interface.get_soliq_token_data())
    if response == 0:
        info_logger.error("soliq_integrations_auth FAILED")
        return 'Сервис временно недоступен, попробуйте позже.'
    
    elif 'token' in str(response):
        return response['token']
    
    return ''


  
def bux_balance_first_form(tin, year, period, loan_portfolio_id, user_id, db_session):
  interface = HttpIntegrationsInterface()

  headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + soliq_integrations_auth()
  }

  body = {
    'lang': 'uz',
    'tin': tin,             
    'year': year,
    'period': period
  }
  response = requestToSoliq("POST", interface.soliq_first_form, headers, {}, json.dumps(body))
  if response == 0:
      info_logger.error("Eror in bux_balance_first_form status_code= %s",ERROR_CODE)
      raise HTTPException(status_code=ERROR_CODE, detail='Сервис временно недоступен, попробуйте позже.')
  if 'message' in response:
      info_logger.error("Eror in bux_balance_first_form status_code = %s, message = %s",ERROR_CODE, response['message'])
      raise HTTPException(status_code=ERROR_CODE, detail=response['message'])
  add_log(loan_portfolio_id, SERVICES.SOLIQ.value, SERVICES_API.SOLIQ_FORM1.value, user_id, interface.soliq_first_form, json.dumps(body), response, db_session)
  return response


def bux_balance_second_form(tin, year, period, loan_portfolio_id, user_id, db_session):
  interface = HttpIntegrationsInterface()

  headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + soliq_integrations_auth()
  }

  body = {
    'lang': 'uz',
    'tin': tin,             
    'year': year,
    'period': period
  }

  response = requestToSoliq("POST", interface.soliq_second_form, headers, {}, json.dumps(body))

  if 'message' in response:
      info_logger.error("Eror in bux_balance_first_form status_code = %s, message = %s",ERROR_CODE, response['message'])
      raise HTTPException(status_code=ERROR_CODE, detail=response['message'])

  add_log(loan_portfolio_id, SERVICES.SOLIQ.value, SERVICES_API.SOLIQ_FORM2.value, user_id, interface.soliq_second_form, json.dumps(body), response, db_session)
  return response



def get_eauksion_orders(request, user_id, db_session):
  
  interface = HttpIntegrationsInterface()

  headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + soliq_integrations_auth()
  }

  body = {
    "language": 'uz',
    "page": request.page,
    "per_page": request.per_page,
    "inn": request.inn,
    "type": request.type
}


  response = requestToSoliq("POST", interface.soliq_get_eauksion_orders, headers, {}, json.dumps(body))

  if 'message' in response:
      info_logger.error("Eror in get_eauksion_orders status_code = %s, message = %s",ERROR_CODE, response['message'])
      raise HTTPException(status_code=ERROR_CODE, detail=response['message'])

  add_log(request.loan_portfolio_id, SERVICES.SOLIQ.value, SERVICES_API.SOLIQ_EAUKSION_GET_ORDERS.value, user_id, interface.soliq_get_eauksion_orders, json.dumps(body), response, db_session)
  return response


def get_eauksion_order_info(request, user_id, db_session):
  
  interface = HttpIntegrationsInterface()

  headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + soliq_integrations_auth()
  }

  body = {
    "language": "uz",
    "order": request.order

}


  response = requestToSoliq("POST", interface.soliq_get_eauksion_order_info, headers, {}, json.dumps(body))

  if 'message' in response:
      info_logger.error("Eror in get_eauksion_order_info status_code = %s, message = %s",ERROR_CODE, response['message'])
      raise HTTPException(status_code=ERROR_CODE, detail=response['message'])

  add_log(request.loan_portfolio_id, SERVICES.SOLIQ.value, SERVICES_API.SOLIQ_EAUKSION_GET_ORDER_INFO.value, user_id, interface.soliq_get_eauksion_order_info, json.dumps(body), response, db_session)
  return response