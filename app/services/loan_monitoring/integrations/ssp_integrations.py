import requests

from app.models.problems_case.problems_assets.problems_assets_notification_model import ProblemsStateNotification
from app.services.loan_monitoring.problems_case.state_chains import set_chain_state_for_ssp
from .http_client.integrations_interface import HttpIntegrationsInterface
from fastapi import HTTPException
import json
from ....config.logs_config import info_logger
from ....models.brief_case.loan_portfolio import Loan_Portfolio
from ....models.integrations.ssp_integrations import SSP_integrations, SSPFiles
from datetime import datetime
from ....common.commit import commit_object, flush_object
from sqlalchemy.sql.expression import cast
import sqlalchemy
import base64
import os
from ....common.dictionaries.integrations_services import SERVICES, SERVICES_API
from .logs import add_log
import uuid
ERROR_CODE = 500


def requestToSSP(method, url, headers, params, data):  
    try:
        response = requests.request(method, url, headers=headers, params=params, data=data, proxies={"http": "", "https": ""})
    except Exception as e:
        info_logger.error(str(e))
        return 0
    #raise {'code':request.status_code, 'errors': 'Unable to connect to server api'}
    return response.json() 



def ssp_integrations_auth():
    interface = HttpIntegrationsInterface()

    headers = {
        'Content-Type': 'application/json'
    }
    response = requestToSSP("POST", interface.ssp_auth, headers,  {}, interface.get_ssp_token_data())
    if response == 0:
        info_logger.error("ssp_integrations_auth FAILED")
        return 'Сервис временно недоступен, попробуйте позже.'
    
    elif 'token' in response:
        return response['token']
    
    return ''



def ssp_theme_list():  
    
    interface = HttpIntegrationsInterface()

    headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + ssp_integrations_auth()
    }

    response = requestToSSP("GET", interface.ssp_theme_list, headers, {}, {})
    if response == 0:
        info_logger.error("Eror in ssp_theme_list status_code= %s",ERROR_CODE)
        raise HTTPException(status_code=ERROR_CODE, detail='Сервис временно недоступен, попробуйте позже.')
    if 'errors' in response:
        info_logger.error("Eror in ssp_theme_list status_code = %s, errors = %s",ERROR_CODE, response['errors'])
        raise HTTPException(status_code=ERROR_CODE, detail=response['errors'])

    return response


def ssp_organization_list():                      
    
    interface = HttpIntegrationsInterface()

    headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + ssp_integrations_auth()
    }

    response = requestToSSP("GET", interface.ssp_organization_list, headers, {}, {})
    if response == 0:
        info_logger.error("Eror in ssp_organization_list status_code= %s",ERROR_CODE)
        raise HTTPException(status_code=ERROR_CODE, detail='Сервис временно недоступен, попробуйте позже.')
    if 'errors' in response:
        info_logger.error("Eror in ssp_organization_list status_code = %s, errors = %s",ERROR_CODE, response['errors'])
        raise HTTPException(status_code=ERROR_CODE, detail=response['errors'])

    return response


def ssp_claim_list():  

    interface = HttpIntegrationsInterface()

    headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + ssp_integrations_auth()
    }

    response = requestToSSP("GET", interface.ssp_claim_list, headers, {}, {})
    if response == 0:
        info_logger.error("Eror in ssp_claim_list status_code= %s",ERROR_CODE)
        raise HTTPException(status_code=ERROR_CODE, detail='Сервис временно недоступен, попробуйте позже.')
    if 'errors' in response:
        info_logger.error("Eror in ssp_claim_list status_code = %s, errors = %s",ERROR_CODE, response['errors'])
        raise HTTPException(status_code=ERROR_CODE, detail=response['errors'])

    return response


def ssp_currency_list():  
    
    interface = HttpIntegrationsInterface()

    headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + ssp_integrations_auth()
    }

    response = requestToSSP("GET", interface.ssp_currency_list, headers, {}, {})
    if response == 0:
        info_logger.error("Eror in ssp_currency_list status_code= %s",ERROR_CODE)
        raise HTTPException(status_code=ERROR_CODE, detail='Сервис временно недоступен, попробуйте позже.')
    if 'errors' in response:
        info_logger.error("Eror in ssp_currency_list status_code = %s, errors = %s",ERROR_CODE, response['errors'])
        raise HTTPException(status_code=ERROR_CODE, detail=response['errors'])

    return response


def ssp_claim_application_get():  
    
    interface = HttpIntegrationsInterface()

    headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + ssp_integrations_auth()
    }

    response = requestToSSP("GET", interface.ssp_claim_application, headers, {}, {})
    if response == 0:
        info_logger.error("Eror in ssp_claim_application status_code= %s",ERROR_CODE)
        raise HTTPException(status_code=ERROR_CODE, detail='Сервис временно недоступен, попробуйте позже.')
    if 'errors' in response:
        info_logger.error("Eror in ssp_claim_application status_code = %s, errors = %s",ERROR_CODE, response['errors'])
        raise HTTPException(status_code=ERROR_CODE, detail=response['errors'])

    return response


def ssp_language_list():  
    
    interface = HttpIntegrationsInterface()

    headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + ssp_integrations_auth()
    }

    response = requestToSSP("GET", interface.ssp_language_list, headers, {}, {})
    if response == 0:
        info_logger.error("Eror in ssp_language_list status_code= %s",ERROR_CODE)
        raise HTTPException(status_code=ERROR_CODE, detail='Сервис временно недоступен, попробуйте позже.')
    if 'errors' in response:
        info_logger.error("Eror in ssp_language_list status_code = %s, errors = %s",ERROR_CODE, response['errors'])
        raise HTTPException(status_code=ERROR_CODE, detail=response['errors'])

    return response


def ssp_integration(id, user_id, db_session):
    
    interface = HttpIntegrationsInterface()

    headers = {  
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + ssp_integrations_auth()
    }
    response = requestToSSP("GET", interface.ssp_integration + str(id), headers, {}, {})
    if response == 0:
        info_logger.error("Eror in ssp_integration status_code= %s",ERROR_CODE)
        raise HTTPException(status_code=ERROR_CODE, detail='Сервис временно недоступен, попробуйте позже.')
    if 'errors' in response:
        info_logger.error("Eror in ssp_integration status_code = %s, errors = %s",ERROR_CODE, response['errors'])
        raise HTTPException(status_code=ERROR_CODE, detail=response['errors'])
    # add_log(SERVICES.SSP.value, SERVICES_API.SSP_CLAIM_APLICATION_GET.value, user_id, interface.ssp_integration + str(id), id, rrrrresponse, db_session)
    return response







import zipfile
import base64
import io


def ssp_claim_application_post(request, user_id,  file_path, db_session):
    files = []
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file in file_path:
            with open(file['name'], 'rb') as fil:
                zip_file.writestr(file['name'], fil.read())

        zip_data = zip_buffer.getvalue()
        encoded_zip = base64.b64encode(zip_data).decode('utf-8')
        files.append({"fileAsBase64":encoded_zip,
                     "fileExtension": '.zip'})
        
    
        # with open(file['name'], "rb") as pdf_file:
        #     base64_pdf = base64.b64encode(pdf_file.read()).decode()
        #     files.append({"fileAsBase64":base64_pdf,
        #                 "fileExtension": os.path.splitext(file['name'])[1]})
    
    interface = HttpIntegrationsInterface()
    headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + ssp_integrations_auth()
    }
    loan_data = db_session.query(Loan_Portfolio.loan_id)\
                                .filter(Loan_Portfolio.id == request.loan_portfolio_id).first()
    
    contractIdentificationNumber = f"MKB_dwh_{uuid.uuid1().int>>64}"
    
    
    document = {
    "claimApplicationTypeId": request.claimApplicationTypeId,
    "claimThemeId": request.claimThemeId,
    "details": request.details,
    "mainDebt": request.mainDebt,
    "calculedPenalty": request.calculedPenalty,
    "penalty": request.penalty,
    "percent": request.percent,
    "currentPrincipalInterest": request.currentPrincipalInterest,
    "currentInterestRate": request.currentInterestRate,
    "otherDebtRepayment": request.otherDebtRepayment,
    "currencyId": request.currencyId,
    "tables": [
        {
        "claimResponsibleTypeId": request.claimResponsibleTypeId,
        "innOrPinfl": request.innOrPinfl,
        "fullName": request.fullName,
        "address": request.address,
        "phoneNumber": request.phoneNumber
        }
    ]
    }
    
    if request.PrevApplicationId is not None:
        document.update({"prevApplicationId": request.PrevApplicationId})
        
    
    if files is not None:
        document.update({"files": files})
    
    
    body = {
    "organizationId": request.organizationId,
    "contractIdentificationNumber": contractIdentificationNumber,
    }
    body.update({"document":document})
    response = requestToSSP("POST", interface.ssp_claim_application, headers, {}, json.dumps(body))
    if response == 0:
        info_logger.error("Eror in ssp_claim_application_post status_code= %s",ERROR_CODE)
        raise HTTPException(status_code=ERROR_CODE, detail='Сервис временно недоступен, попробуйте позже.')
    if 'errors' in response:
        info_logger.error("Eror in ssp_claim_application_post status_code = %s, errors = %s",ERROR_CODE, response['errors'])
        raise HTTPException(status_code=ERROR_CODE, detail=response['errors'])

    new_ssp_aplication = SSP_integrations(loan_portfolio_id = request.loan_portfolio_id,
                                        request_id = response['id'],
                                        contractIdentificationNumber = contractIdentificationNumber,
                                        claimThemeId = request.claimThemeId,
                                        claimResponsibleTypeId = request.claimResponsibleTypeId,
                                        claimApplicationTypeId = request.claimApplicationTypeId,
                                        mainDebt = request.mainDebt,
                                        calculedPenalty = request.calculedPenalty,
                                        penalty = request.penalty,
                                        percent = request.percent,
                                        currentPrincipalInterest = request.currentPrincipalInterest,
                                        currentInterestRate = request.currentInterestRate,
                                        otherDebtRepayment = request.otherDebtRepayment,
                                        currencyId = request.currencyId,
                                        details = request.details,
                                        created_at = datetime.now())
    db_session.add(new_ssp_aplication)
    flush_object(db_session)
    
    for file in file_path:
        new_ssp_file = SSPFiles(ssp_id = new_ssp_aplication.id,
                                file_url = file['name'],
                                created_at =  datetime.now())
        db_session.add(new_ssp_file)
        commit_object(db_session)
    
    
    
    add_log(request.loan_portfolio_id, SERVICES.SSP.value, SERVICES_API.SSP_CLAIM_APLICATION_POST.value, user_id, interface.ssp_claim_application, json.dumps(body), response, db_session)
    set_chain_state_for_ssp(loan_data.loan_id, db_session)
    
    get_problems_state_notification = db_session.query(ProblemsStateNotification).filter(ProblemsStateNotification.loan_portfolio_id == request.loan_portfolio_id).first()
    if get_problems_state_notification is None:
        new_problems_state_notification = ProblemsStateNotification(loan_portfolio_id = request.loan_portfolio_id, tpp_status = True)
        db_session.add(new_problems_state_notification)
        flush_object(db_session)
    else:
        get_problems_state_notification.tpp_status = True
    
    commit_object(db_session)
    return {"OK"}

def get_requests_by_loan(loan_id, db_session):
    ssp_data = []
    get_ssp_data =  db_session.query(SSP_integrations)\
        .filter(SSP_integrations.loan_portfolio_id == loan_id).order_by(SSP_integrations.created_at.desc()).all()
        
    for ssp in get_ssp_data:
        ssp_data.append({"id": ssp.id,
                       "request_id": ssp.request_id,
                       "claimApplicationTypeId":ssp.claimApplicationTypeId,
                       "created_at": ssp.created_at,
                       "files": ssp.files})
        
        
    return ssp_data


def get_data_for_post(loan_portfolio_id, db_session):
    loan_data = db_session.query(Loan_Portfolio.loan_id,
                                cast(Loan_Portfolio.balance_16397, sqlalchemy.FLOAT).label('balance_16397'), 
                                cast(Loan_Portfolio.overdue_balance, sqlalchemy.FLOAT).label('overdue_balance'), 
                                cast(Loan_Portfolio.balance_16323, sqlalchemy.FLOAT).label('balance_16323'), 
                                cast(Loan_Portfolio.balance_16309, sqlalchemy.FLOAT).label('balance_16309'),
                                cast(Loan_Portfolio.balance_16325, sqlalchemy.FLOAT).label('balance_16325'),
                                cast(Loan_Portfolio.balance_16377, sqlalchemy.FLOAT).label('balance_16377'),
                                cast(Loan_Portfolio.credit_account_balance, sqlalchemy.FLOAT).label('credit_account_balance'))\
                                .filter(Loan_Portfolio.id == loan_portfolio_id).first()
    return {
            "mainDebt": loan_data.overdue_balance,
            "calculedPenalty": loan_data.balance_16377 and loan_data.balance_16377 or 0,
            "penalty": loan_data.credit_account_balance and loan_data.credit_account_balance or 0,
            "percent": loan_data.balance_16397 and loan_data.balance_16397 or 0,
            "currentInterestRate": (loan_data.balance_16323 and loan_data.balance_16323 or 0)\
                                + (loan_data.balance_16309 and loan_data.balance_16309 or 0)\
                                + (loan_data.balance_16325 and loan_data.balance_16325 or 0)
            }