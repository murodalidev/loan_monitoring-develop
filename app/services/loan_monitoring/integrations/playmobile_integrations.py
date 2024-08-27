import requests
from .http_client.integrations_interface import HttpIntegrationsInterface
from fastapi import HTTPException
from ..monitoring_case.script_date_holidays import define_is_the_date_holiday_or_weekend
import uuid
import json

SENDER_NAME = "3900"

def requestToPlaymobile(method, url, headers, params, data, proxies=None):
  try:
    request = requests.request(method, url, headers=headers, proxies=proxies, params=params, data=data)
    response = request.text
  except:
    return {'code':500, 'msg': 'Unable to connect to server api'}
  
  return response      
  
def send_sms_playmobile(phone_number, text):
  interface = HttpIntegrationsInterface()

  headers = {
    'Content-Type': 'application/json',
    'Api-Token': interface.get_playmobile_token()
  }
  proxies = { 
              "http"  : 'http://10.5.49.208:8080', 
              "https" : 'http://10.5.49.208:8080'
            }
  body = {
     "messages": [
        {
            "recipient": phone_number,
            "message-id": str(uuid.uuid4())[:10],
            "sms": {
                "originator": SENDER_NAME,
                "content": {
                    "text": text
                }
            }
        }
     ]
  }
  response = requestToPlaymobile("POST", interface.playmobile_send, headers, proxies, {}, json.dumps(body))
  if 'code' in response:
        return HTTPException(status_code=response['code'], detail=response['msg'])

  return response
  
  
  
  
from datetime import datetime, timedelta
from sqlalchemy import and_, or_
from sqlalchemy.sql.expression import extract
from sqlalchemy.sql import text
import time
from ....models.brief_case.loan_portfolio import Loan_Portfolio
from ....models.brief_case.loan_portfolio_schedule import LoanPortfolioSchedule
from ....models.balance_turnover.balance_turnover_model import Accounts, BalanceTurnover
from ....models.balance_turnover.account_prefix_model import AccountPrefix
from ....common.commit import commit_object, flush_object
from ....common.is_empty import is_empty, is_empty_list  
  
  
  
  
def send_sms_to_clients(db_session):
  interval_3_days = datetime.now().date()
  while define_is_the_date_holiday_or_weekend(interval_3_days, db_session) is False:
        interval_3_days = interval_3_days + timedelta (days = 1)
        print(interval_3_days)
  get_clients = db_session.query(Loan_Portfolio.mobile_phone).join(LoanPortfolioSchedule, LoanPortfolioSchedule.loan_id==Loan_Portfolio.loan_id)\
    .filter(LoanPortfolioSchedule.date_red==interval_3_days).filter(Loan_Portfolio.status==1).filter(Loan_Portfolio.mobile_phone!=None).all()
    
  
  
  
  