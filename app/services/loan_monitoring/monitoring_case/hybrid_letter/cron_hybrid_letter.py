from datetime import datetime, timedelta
from app.models.brief_case.loan_portfolio import Loan_Portfolio
from sqlalchemy.orm import aliased
from app.models.kad_case.kad_case_model import KADCase
from .....models.loan_case.loan_case_model import LoanCase
from .....models.monitoring_case.hybrid_letter_model import HybridLetters
from .....models.monitoring_case.monitoring_case_model import MonitoringCase
from .....models.monitoring_case.target_monitoring_model import TargetMonitoring
from .....models.monitoring_task_manager.task_manager_model import TaskManager
from .....common.commit import commit_object, flush_object
from .....common.dictionaries.monitoring_case_dictionary import loan_case, letter_status
from .....schemas.notification_schemas import CreateNotification
from ...notification.notification_crud import Notificaton_class
from .....common.dictionaries import notification_dictionary
from . import hybrid_letter
from ..script_date_holidays import get_business_days
from .....common.dictionaries.general_tasks_dictionary import MGT, KGT
from  app.services.loan_monitoring.monitoring_case.script_date_holidays import get_business_days
from sqlalchemy import or_, and_
from .....config.logs_config import info_logger
from .....schemas.problems_case_schemas import  GenerateLetter, SendLetter
from sqlalchemy.sql import text
from datetime import datetime, timedelta
from app.models.brief_case.directories.bank_mfo import bank_mfo

from app.models.brief_case.directories.client_region import client_region
from app.models.brief_case.loan_portfolio_schedule import LoanPortfolioSchedule

from .....models.brief_case.directories.local_code import local_code
from .....models.brief_case.loan_portfolio import Loan_Portfolio
from .....models.loan_case.loan_case_model import LoanCase
from .....models.brief_case.directories.dis_reg_post_codes import post_codes
from .....models.brief_case.directories.client_district import client_district
from .http_client.hybrid_letter_client import HybridLetterClient
from .post_request import HTTPClient
from fastapi import HTTPException
from .....models.monitoring_case.hybrid_letter_model import HybridLetters

from .....common.commit import commit_object, flush_object
from sqlalchemy.orm import aliased
from .....schemas.notification_schemas import CreateNotification
from ...notification.notification_crud import Notificaton_class
from .....common.dictionaries import notification_dictionary
from fastapi.responses import FileResponse
from app.db.connect_db import SessionManager
import time





def cron_send_letter_schedule(start, end, db_session):
    # db_session.execute(text(f'ALTER SEQUENCE hybrid_letters_id_seq RESTART WITH 1'))
    # db_session.commit()
    # exit()
    info_logger.info(f'Started sending 35 day letters')
    cron_send_letter(start, end, db_session)
    info_logger.info(f'Finished sending 35 day letters')
    info_logger.info(f'Started sending 45 day letters')
    cron_send_letter(start, end, db_session)
    info_logger.info(f'Finished sending 45 day letters')

def cron_send_letter(start, end, db_session):
    send_letter = None
    get_loans = db_session.execute(text(f'''SELECT 
                                                KC.ID,
                                                LP.ID AS PORTFOLIO_ID,
                                               LP.LOAN_ID,
                                               LP.BORROWER_TYPE,
                                               LC.NAME AS LOCAL_NAME,
                                               LP.CLIENT_NAME,
                                               CR.NAME AS REGION,
                                               CD.NAME AS CLIENT_DISTRICT,
                                               LP.CLIENT_ADDRESS,
                                               LP.ISSUE_DATE,
                                               LP.MATURITY_DATE,
                                               LP.CREDIT_LINE_PURPOSE AS LOAN_PURPOSE,
                                               LP.OSN_CMP_PERCENT AS PERCENT,
                                               LP.CONTRACT_AMOUNT_UZ_CURRENCY AS LOAN_AMOUNT,
                                               LP.TOTAL_OVERDUE,
                                               LP.OVERDUE_BALANCE,
                                               LP.BALANCE_16377
                                        FROM KAD_CASE KC
                                        LEFT JOIN LOAN_PORTFOLIO LP ON KC.LOAN_PORTFOLIO_ID=LP.ID
                                        LEFT JOIN LOCAL_CODE LC ON LC.ID=LP.LOCAL_CODE_ID
                                        LEFT JOIN CLIENT_REGION CR ON CR.ID=LP.CLIENT_REGION
                                        LEFT JOIN CLIENT_DISTRICT CD ON CD.CODE = LP.CLIENT_DISTRICT
                                        
                                        WHERE ((LP.DATE_OVERDUE_PERCENT IS NULL
                                                AND LP.OVERDUE_START_DATE IS NOT NULL
                                                AND (CURRENT_DATE - LP.OVERDUE_START_DATE >= {start}
                                                AND CURRENT_DATE - LP.OVERDUE_START_DATE < {end}))
                                        OR (LP.OVERDUE_START_DATE IS NULL
                                                AND LP.DATE_OVERDUE_PERCENT IS NOT NULL
                                                AND (CURRENT_DATE - LP.DATE_OVERDUE_PERCENT >= {start}
                                                AND CURRENT_DATE - LP.DATE_OVERDUE_PERCENT < {end}))
                                        OR (LP.DATE_OVERDUE_PERCENT IS NOT NULL
                                                AND LP.OVERDUE_START_DATE IS NOT NULL
                                                AND LP.OVERDUE_START_DATE < LP.DATE_OVERDUE_PERCENT
                                                AND (CURRENT_DATE - LP.OVERDUE_START_DATE >= {start}
                                                AND CURRENT_DATE - LP.OVERDUE_START_DATE < {end}))
                                        OR (LP.DATE_OVERDUE_PERCENT IS NOT NULL
                                                AND LP.OVERDUE_START_DATE IS NOT NULL
                                                AND LP.OVERDUE_START_DATE >= LP.DATE_OVERDUE_PERCENT
                                                AND (CURRENT_DATE - LP.DATE_OVERDUE_PERCENT >= {start}
                                                AND CURRENT_DATE - LP.DATE_OVERDUE_PERCENT < {end})))
                                        AND LP.IS_TAKEN_KAD=TRUE
                                        AND KC.KAD_CASE_STATUS_ID != 2
                                        AND LP.STATUS = 1
                                        
                                        
                                        ORDER BY KC.ID
                                        ''')).fetchall()
    
    
    #info_logger.info(get_loans)
    for kad in get_loans:
        get_schedule = db_session.execute(text(f'SELECT DATE_RED FROM LOAN_PORTFOLIO_SCHEDULE WHERE LOAN_ID = {kad.loan_id} AND DATE_RED IS NOT NULL')).fetchone()
        schedule_day = None
        if get_schedule is not None:
            schedule_day = get_schedule.date_red.day
        issue_date = None
        maturity_date = None
        loan_period = None
    
    
        if kad.issue_date is not None:
            issue_date = kad.issue_date
        if kad.maturity_date is not None:
            maturity_date = kad.maturity_date
        if issue_date is not None and maturity_date is not None:
            loan_period = diff_month(maturity_date, issue_date)
            
            
        get_hybrid_letter = db_session.query(HybridLetters).filter(HybridLetters.kad_case_id == kad.id)
        
        if start == 35:
            get_hybrid_letter = get_hybrid_letter.filter(HybridLetters.general_task_id == KGT.SEND_1_LETTER.value).first()
            letter_general_task_id = KGT.SEND_1_LETTER.value
        else:
            get_hybrid_letter = get_hybrid_letter.filter(HybridLetters.general_task_id == KGT.SEND_2_LETTER.value).first()
            letter_general_task_id = KGT.SEND_2_LETTER.value
        if get_hybrid_letter == None:
            
            #letter_data_for_generate = hybrid_letter.get_details_for_send(kad.loan_id, db_session)
            letter_data = GenerateLetter()
            overdue_balance = 0
            if kad.overdue_balance is not None:
                overdue_balance = float(kad.overdue_balance)
            balance_16377 = 0
            if kad.balance_16377 is not None:
                balance_16377 = float(kad.balance_16377)
            letter_data.letter_receiver_type_id = 1
            letter_data.local_name = kad.local_name
            letter_data.client_name = kad.client_name
            letter_data.client_region = kad.region
            letter_data.client_district = kad.client_district
            letter_data.client_address = kad.client_address
            letter_data.issue_date = kad.issue_date
            letter_data.loan_id = kad.loan_id
            letter_data.loan_purpose = kad.loan_purpose
            letter_data.loan_period = loan_period
            letter_data.percent = kad.percent
            letter_data.loan_amount = kad.loan_amount
            letter_data.schedule_day = schedule_day
            letter_data.total_overdue = kad.total_overdue
            letter_data.overdue_balance = overdue_balance
            letter_data.balance_16377 = balance_16377
            letter_data.total_balance = overdue_balance + balance_16377
            letter_data.branch_region = kad.region
            letter_data.borrower_type = kad.borrower_type
            letter_data.kad_case_id = kad.id
            letter_data.general_task_id = letter_general_task_id
            letter_data.cur_date = datetime.now().date()
            hybrid = hybrid_letter.generate_letter_for_schedule(letter_data, db_session)
            
            
            if kad.local_name is None or kad.client_name is None or\
                kad.region is None or kad.client_district is None or\
                    kad.client_address is None or kad.issue_date is None or\
                        kad.loan_purpose is None or loan_period is None or\
                            kad.percent is None or kad.loan_amount is None or\
                                schedule_day is None or kad.total_overdue is None or\
                                     kad.client_district is None:
                info_logger.info(f'There is no data to generate the file')
                hybrid['letter'].error_comment = 'Отсутствуют данные для генерации файла'
                hybrid['letter'].letter_status_id = letter_status['ошибка']
                commit_object(db_session)
                continue
            else:
                send_letter = SendLetter()
                send_letter.loan_portfolio_id = kad.portfolio_id
                send_letter.kad_case_id = kad.id
                send_letter.general_task_id = letter_general_task_id
                hybrid_letter.send_letter(send_letter, db_session, kad.loan_id)
                
        elif  get_hybrid_letter.letter_status_id == letter_status['новый'] or get_hybrid_letter.letter_status_id == letter_status['ошибка']:
            
            send_letter = SendLetter()
            send_letter.loan_portfolio_id = kad.portfolio_id
            send_letter.kad_case_id = kad.id
            send_letter.general_task_id = letter_general_task_id
            hybrid_letter.send_letter(send_letter, db_session, kad.loan_id)
        
    
    
    
    return {"OK"}



def diff_month(d1, d2):
        return (d1.year - d2.year) * 12 + d1.month - d2.month