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
from ....common.decorator import measure_time

import re  
    
    
def validate_phone_number(phone):
        

    validate_phone_number_pattern = "^\\+?[1-9][0-9]{7,14}$"
    res = re.match(validate_phone_number_pattern, phone)
    if res:
        return True
    return False



@measure_time
def load_client_data(orc_session, db_session):
    start_timer = time.time()
    p_size = 1000
    page = 1
    i=0
    #today = str((datetime.now()-timedelta(days=1)).date().strftime("%d-%m-%Y")).replace('-','.')
    Accountprefixes = db_session.query(AccountPrefix).all()
   # prefixes1 = [x.code for x in Accountprefixes]
    #mainPrfixes = db_session.execute(text('select distinct substring(debt_account, 1, 5) as debt_account_prifix from loan_portfolio where debt_account is not null')).fetchall()
    #prefixes2 = [x[0] for x in mainPrfixes]
    #prefixes = prefixes1 + prefixes2
    query = db_session.query(Loan_Portfolio.loan_id).filter(Loan_Portfolio.status==1).filter(Loan_Portfolio.mobile_phone==None)
    size = query.count()
    for page in range(1, int(size/1000)+2):
        i=i+1
        query = db_session.query(Loan_Portfolio.loan_id).filter(Loan_Portfolio.status!=3).limit(p_size).offset((page-1)*p_size)
        loan_ids = query.all()
        
        loans = [x[0] for x in loan_ids]
        result = orc_session.execute(text(f'''
                                    SELECT LC.LOAN_ID,
                                    CC.NAME,
                                    CC.ADDRESS,
                                    CC.PHONE,
                                    CC.MOBILE_PHONE,
                                    CC.SUBJECT
                                FROM IBS.LN_CARD@IABS_PROD.MKB.UZ LC
                                LEFT JOIN IBS.CLIENT_CURRENT@IABS_PROD.MKB.UZ CC ON CC.CODE = LC.CLIENT_CODE
                                AND CC.CLIENT_UID = LC.CLIENT_UID
                                AND CC.ID = LC.CLIENT_ID
                                WHERE LC.LOAN_ID IN {tuple(loans)}
                                            ''')).fetchall()
        print(i*1000)
        for res in result:
            
            get_portfolio = db_session.query(Loan_Portfolio).filter(Loan_Portfolio.loan_id==res.loan_id).first()
            
            get_portfolio.client_address == res.address
            get_portfolio.phone == res.phone
            get_portfolio.mobile_phone = res.mobile_phone

            
            
            flush_object(db_session)
            
    commit_object(db_session)
    end_timer = time.time()
    res = end_timer - start_timer
    final_res = res / 60
    print(f'Execution time: {final_res} minutes')
    return 0







@measure_time
def load_loan_schedule(orc_session, db_session):
    start_timer = time.time()
    
    i=0
    portfolio = db_session.execute(text(f'''
                                    select lp.loan_id from loan_portfolio lp where lp.loan_id not in (select distinct lsc.loan_id from loan_portfolio_schedule lsc) and lp.status=1
                                            ''')).fetchall()
        
    
    
    for loan in portfolio:
        i=i+1
        
        result = orc_session.execute(text(f'''
                                    select * 
                                    from ibs.ln_graph_debt@iabs_prod.mkb.uz l 
                                    where l.loan_id = {loan[0]}
                                            ''')).fetchall()
        
        if i%1000==0:
            #commit_object(db_session)
            print(i)
        schedule = db_session.query(LoanPortfolioSchedule).filter(LoanPortfolioSchedule.loan_id==result[0].loan_id).all()
        
        
        for res in result:
            
            if schedule == []:
                new_schedule = LoanPortfolioSchedule(
                            uuid = res.id,
                            loan_id = res.loan_id,
                            date_red = res.date_red,
                            summ_red = res.summ_red,
                            sign_long = res.sign_long,
                            condition = res.condition, 
                            date_modify = res.date_modify,
                            created = datetime.now())
                db_session.add(new_schedule)
                
           
            flush_object(db_session)
    commit_object(db_session)
    
    end_timer = time.time()
    res = end_timer - start_timer
    final_res = res / 60
    print(f'Execution time: {final_res} minutes')
    return 'OK'
    
    
    
    
    
    
    
    # for page in range(1, int(size/100)+2):
    #     i=i+1
    #     portfolio = db_session.query(Loan_Portfolio.loan_id).filter(Loan_Portfolio.status!=3)\
    #         .limit(p_size).offset((page-1)*p_size)
            
    #     loan_ids = portfolio.all()
        
    #     loans = [x[0] for x in loan_ids]
    #     result = orc_session.execute(text(f'''
    #                                 select * 
    #                                 from ibs.ln_graph_debt@iabs_prod.mkb.uz l 
    #                                 where l.loan_id in {tuple(loans)}
    #                                         ''')).fetchall()
        
    #     if i%100==0:
    #         commit_object(db_session)
    #         print(i)
    #     for res in result:
            
           
    #         new_schedule = LoanPortfolioSchedule(
    #                     uuid = res.id,
    #                     loan_id = res.loan_id,
    #                     date_red = res.date_red,
    #                     summ_red = res.summ_red,
    #                     sign_long = res.sign_long,
    #                     condition = res.condition, 
    #                     date_modify = res.date_modify,
    #                     created = datetime.now())
    #         db_session.add(new_schedule)
                
           
    #         flush_object(db_session)
    
    
    
    
    
    
    
