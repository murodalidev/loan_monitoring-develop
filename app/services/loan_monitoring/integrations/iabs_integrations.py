import requests
import datetime
from app.models.brief_case.directories.currency import currency as Currency
from app.models.integrations.currency_model import CurrencyRate
from .http_client.integrations_interface import HttpIntegrationsInterface
from ....models.brief_case.loan_portfolio import Loan_Portfolio
from ....models.brief_case.loan_portfolio_schedule import LoanPortfolioSchedule
from fastapi import HTTPException
import uuid
from ....config.logs_config import info_logger
from ....common.commit import commit_object, flush_object

headers = {
    'Accept-Language': 'en',
    'Content-Type': 'application/json',
    'requestId': str(uuid.uuid4())[:10],
    'Authorization': ''
}

def requestToIabs(method, url, headers, params, data, count):
    # timeout = 30 sec, we are doing the request 3 times
    try:
      request = requests.request(method, url, headers=headers, params=params, data=data, timeout=30.0)
      response = request.json()
    except:
      count += 1
      if count <= 3:
        info_logger.info("Timeout, try ", count, " times")
        return requestToIabs(method, url, headers, params, data, count)
      else :
        info_logger.info("Unable to connect to server api, ", url)
        return 0
    
    return response      
  

def iabs_integrations_auth(interface):
    #interface = HttpIntegrationsInterface()
    
    response = requestToIabs("POST", interface.iabs_auth, headers, {}, interface.get_token_data(), 1)
    if response == 0:
      return 'Сервис временно недоступен, попробуйте позже.'
    if 'code' in response:
      return {'code':{response['code']}, 'msg': {response['msg']}}
    
    headers['Authorization'] = 'Bearer ' + response['token']
    headers['requestId'] =  str(uuid.uuid4())[:10]

    return response


# loan1 -  Кредитный счет loan_account +
# saldo1 - Остаток кредитного счета credit_account_balance +
# loan2 - Расчетный счет checkingAccount -;
# saldo2 - Остаток расчетного счета checking_account_balance +
# loan3 - Счет Для Начисления Процентов  По Текущей Задолженности currentPercentDebtAccount -
# saldo3 - balance_16309 +
# loan5 - Счет просрочки debt_account +
# saldo5 - Остаток просрочки overdue_balance +
# loan7 -  Счет начисления процента по просроченной ссуде overdueLoanInterestAccount -
# saldo7 - Остаток процента по просроченной ссуде percentBalanceOnOverdueLoan -
# loan46 - Cчет просрочки процента InterestOverdueAccount -
# saldo46 - balance_16377 +
# overdueDebt - Просроченный долг overdueDebt -
# accruedOverDueInterest - Начисленные просроченные проценты accruedOverDueInterest -

def get_client_credit(db_session, loanId: int):
    interface = HttpIntegrationsInterface()
    authRes = iabs_integrations_auth(interface)
    if 'status_code' in authRes:
      raise HTTPException(status_code=403, detail=f"{authRes['msg']} status code: {authRes['status_code']}")
    response = requestToIabs("GET", interface.iabs_get_client_credit + str(loanId), headers, {}, {}, 1)
    if response == 0:
      return HTTPException(status_code=500, detail='Сервис временно недоступен, попробуйте позже.')
    if 'code' in response and response['code'] != 0:
      raise HTTPException(status_code=403, detail=f"{response['msg']} -  code: {response['code']}")

    array_data = response['responseBody']['data']
    if len(array_data) == 0:
      raise HTTPException(status_code=404, detail="Нет данных по loanId")
    data = array_data[0]
    get_portfolio = db_session.query(Loan_Portfolio).filter(Loan_Portfolio.loan_id == loanId).first()
    get_portfolio.loan_account = data['loan1']
    get_portfolio.credit_account_balance = data['saldo1'] and float(data['saldo1'])/100
    get_portfolio.checkingAccount = data['loan2']
    get_portfolio.checking_account_balance = data['saldo2']
    get_portfolio.current_percent_debt_account = data['loan3']
    get_portfolio.balance_16309 = data['saldo3'] and float(data['saldo3'])/100
    get_portfolio.debt_account = data['loan5']
    get_portfolio.overdue_balance = data['saldo5'] and float(data['saldo5'])/100
    get_portfolio.overdue_loan_interest_account = data['loan7']
    get_portfolio.percent_balance_on_overdue_loan = data['saldo7'] and float(data['saldo7'])/100
    get_portfolio.interest_overdue_account = data['loan46']
    get_portfolio.balance_16377 = data['saldo46'] and float(data['saldo46'])/100
    get_portfolio.overdue_debt = data['overdueDebt'] and float(data['overdueDebt'])/100
    get_portfolio.accruedOverDueInterest = data['accruedOverDueInterest'] and float(data['accruedOverDueInterest'])/100

    commit_object(db_session)

    return ['OK']


def get_customer(db_session, pinfl: int, loan_portfolio_id: int):
    interface = HttpIntegrationsInterface()
    authRes = iabs_integrations_auth(interface)

    if 'status_code' in authRes:
      raise HTTPException(status_code=403, detail=f"{authRes['msg']} -  code: {authRes['status_code']}")

    response = requestToIabs("GET", interface.iabs_get_customer, headers, {"pnfl": pinfl}, {}, 1)

    if 'code' in response and response['code'] != 0:
      raise HTTPException(status_code=403, detail=f"{response['msg']} -  code: {response['code']}")

    data = response['responseBody']['response'][0]
    get_portfolio = db_session.query(Loan_Portfolio).filter(Loan_Portfolio.id == loan_portfolio_id).first()

    get_portfolio.client_uid = data['clientUid']
    get_portfolio.phone = data['phone']
    get_portfolio.mobile_phone = data['mobilePhone']

    commit_object(db_session)


    return data['clientUid']


def get_corporate_customer(db_session, inn: int, loan_portfolio_id: int):
    interface = HttpIntegrationsInterface()
    authRes = iabs_integrations_auth(interface)

    if 'status_code' in authRes:
      return HTTPException(status_code=authRes['status_code'], detail=authRes['msg'])


    response = requestToIabs("GET", interface.iabs_get_corporate_customer, headers, {"tin": inn}, {}, 1)

    if 'code' in response and response['code'] != 0:
      return HTTPException(status_code=response['code'], detail=response['msg'])

    data = response['responseBody']
    get_portfolio = db_session.query(Loan_Portfolio).filter(Loan_Portfolio.id == loan_portfolio_id).first()

    get_portfolio.client_uid = data['clientUid']
    get_portfolio.phone = data['phone']
    get_portfolio.mobile_phone = data['mobilePhone']

    commit_object(db_session)

    return data['clientUid']




def get_currency_rate(db_session):
  interface = HttpIntegrationsInterface()
  authRes = iabs_integrations_auth(interface)

  if 'status_code' in authRes:
    return HTTPException(status_code=authRes['status_code'], detail=authRes['msg'])


  response = requestToIabs("GET", interface.iabs_get_currency_rate_jur, headers, {}, {}, 1)
  
  if 'code' in response and response['code'] != 0:
    return HTTPException(status_code=response['code'], detail=response['msg'])
  if response['responseBody']['result']!=[]:
    if_exists = db_session.query(CurrencyRate.id).filter(CurrencyRate.date == datetime.datetime.now().date()).first()
    if if_exists is None:
      for currency in response['responseBody']['result']:
        get_currency_code = db_session.query(Currency.id).filter(Currency.code == currency['code']).first()
        new_currency = CurrencyRate(
          equival = float(str(currency['equival']).replace(' ','')),
          name = currency['name'],
          code = get_currency_code.id,
          request_id = headers['requestId']
        )
    
        db_session.add(new_currency)
        flush_object(db_session)
    else: print('exists')

  commit_object(db_session)

  return 0






def get_active_accounts(clientId: int, codeFilial):
    interface = HttpIntegrationsInterface()
    authRes = iabs_integrations_auth(interface)

    if 'status_code' in authRes:
      return HTTPException(status_code=authRes['status_code'], detail=authRes['msg'])


    response = requestToIabs("GET", interface.iabs_get_accounts + str(clientId), headers, {}, {}, 1)

    if 'code' in response and response['code'] != 0:
      return HTTPException(status_code=response['code'], detail=response['msg'])

    data = response['responseBody']['response']
    # get_portfolio = db_session.query(Loan_Portfolio).filter(Loan_Portfolio.id == loan_portfolio_id).first()
    # if get_portfolio.client_uid == None:
    #   if(get_portfolio.borrower_type != None):
    #     if(get_portfolio.borrower_type[0:3] == '08'):
    #       get_corporate_customer(db_session, )



    def get_acc_by_mfo(account):
      if account['codeFilial'] == codeFilial:
        return True
      return False

    data = list(filter(get_acc_by_mfo, data))

    return data



def get_account_turnover_for_loan(account: str, codeFilial: str, dateBegin: str, dateClose: str): 
    interface = HttpIntegrationsInterface()
    authRes = iabs_integrations_auth(interface)

    if 'status_code' in authRes:
      return HTTPException(status_code=authRes['status_code'], detail=authRes['msg'])


    params = interface.get_account_turnover_params(account, codeFilial, dateBegin, dateClose)
    response = requestToIabs("GET", interface.iabs_get_account_turnover_for_loan, headers, params, {}, 1)
    data = response['responseBody']['response']


    if 'code' in response and response['code'] != 0:
      return HTTPException(status_code=response['code'], detail=response['msg'])

    return data

def get_loan_repayment_schedule(db_session, loan_id: str):
    check_exist = db_session.query(LoanPortfolioSchedule).filter(LoanPortfolioSchedule.loan_id == loan_id).first()

    if check_exist is not None:
       return ["Schedule for this loanId is already exist"]
    
    interface = HttpIntegrationsInterface()
    authRes = iabs_integrations_auth(interface)

    if 'status_code' in authRes:
      return HTTPException(status_code=authRes['status_code'], detail=authRes['msg'])

    response = requestToIabs("GET", f'{interface.iabs_get_loan_repayment_schedule}/{loan_id}', headers, {} , {}, 1)

    if 'code' in response and response['code'] != 0:
      return HTTPException(status_code=response['code'], detail=response['msg'])
    
    schedule_data = response['responseBody']['data']

    for data in schedule_data:  
        [day, month, year] = data['repaymentDate'].split('.')

        schedule = LoanPortfolioSchedule(
          loan_id = loan_id,
          repayment_date = datetime.date(int(year), int(month), int(day)),
          amount = data['amount'] and data['amount'] or None,
          interest_on_term_debt = data['interestOnTermDebt'] and data['interestOnTermDebt'] or None,
          recommended_amount = data['recommendedAmount'] and data['recommendedAmount'] or None,
          saldo = data['saldo'] and data['saldo'] or None,
          created = datetime.datetime.now(),
        )

        db_session.add(schedule)

    commit_object(db_session)

    return ['OK']