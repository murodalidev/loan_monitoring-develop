from datetime import datetime, timedelta, date
from sqlalchemy import or_, and_, func, case
import sqlalchemy
from sqlalchemy.sql.expression import cast, extract
from sqlalchemy.sql.expression import extract
from sqlalchemy.sql import text

from app.models.integrations.currency_model import CurrencyRate
from .....config.logs_config import cron_logger
from .....models.brief_case.loan_portfolio import Loan_Portfolio, Loan_Portfolio_Date
from .....models.brief_case.loan_portfolio_schedule import LoanPortfolioSchedule
from .....models.balance_turnover.balance_turnover_model import Accounts, BalanceTurnover, CheckBalanceTurnoverUpdate, Saldo, CheckBalanceTurnoverUpdatePerOperDay
from .....models.balance_turnover.account_prefix_model import AccountPrefix
from .....common.commit import commit_object, flush_object
from .....common.decorator import measure_time
from ...monitoring_case.script_date_holidays import define_is_the_date_holiday_or_weekend
from .....common.is_empty import is_empty, is_empty_list, is_exists

@measure_time
def load_accounts(orc_session, day, db_session):
    p_size = 1000
    page = 1
    i=0
    result = None
    if day is None:
        day=1
    day = (datetime.now()-timedelta(days=day)).date()
    print(day)
    today = str(day.strftime("%d-%m-%Y")).replace('-','.')
    is_exists = db_session.query(Saldo.id).filter(Saldo.oper_day == day).first()
    if is_exists is None:
        Accountprefixes = db_session.query(AccountPrefix).all()
        debtPrfixes = db_session.execute(text('select distinct substring(debt_account, 1, 5) as debt_account_prifix from loan_portfolio where debt_account is not null and status = 1')).fetchall()
        juridicalPrfixes = db_session.execute(text('select distinct substring(judicial_account, 1, 5) as judical_account from loan_portfolio where judicial_account is not null and status = 1')).fetchall()
        balancePrfixes = db_session.execute(text('select distinct balance_account as balance_account from loan_portfolio where balance_account is not null and status = 1')).fetchall()
        #[x.code for x in Accountprefixes] + [x[0] for x in debtPrfixes] +
        prefixes = [x.code for x in Accountprefixes] + [x[0] for x in debtPrfixes] +  [x[0] for x in juridicalPrfixes] + [x[0] for x in balancePrfixes]
        query = db_session.query(Loan_Portfolio.loan_id).filter(Loan_Portfolio.status==1)
        size = query.count()
        for page in range(1, int(size/1000)+2):
            i=i+1
            loan_ids = db_session.query(Loan_Portfolio.loan_id).filter(Loan_Portfolio.status==1).order_by(Loan_Portfolio.id.asc()).limit(p_size).offset((page-1)*p_size).all()
            
            loans = [x[0] for x in loan_ids]
            try:
                result = orc_session.execute(text(f'''
                                        SELECT 
                                            L.LOAN_TYPE_ACCOUNT,
                                            L.COA,L.LOAN_ID,
                                            A.ID,
                                            A.ACCOUNT_CODE, 
                                            A.CODE_FILIAL,
                                            --A.CODE,
                                            A.SALDO_IN,
                                            A.SALDO_OUT,
                                            A.TURNOVER_DEBIT,
                                            A.TURNOVER_CREDIT,
                                            A.TURNOVER_ALL_DEBIT,
                                            A.TURNOVER_ALL_CREDIT,
                                            A.OPER_DAY
                                        FROM IBS.LN_ACCOUNT@IABS_PROD.MKB.UZ L,
                                            IBS.SALDO@IABS_PROD.MKB.UZ A
                                        WHERE 
                                        L.LOAN_ID IN {tuple(loans)}
                                        AND L.COA IN {tuple(prefixes)}
                                            AND 
                                            L.ACCOUNT_CODE = A.ACCOUNT_CODE
                                            AND (A.TURNOVER_DEBIT <> 0 or A.TURNOVER_CREDIT <> 0)
                                            AND L.FILIAL_CODE = A.CODE_FILIAL
                                            AND A.OPER_DAY = TO_DATE('{today}','DD.MM.YYYY')
                                                ''')).fetchall()
            
            except Exception as e:
                cron_logger.info(str(e))
                
            print(len(result))
            if result is not None:
                for res in result:
                    new_account = Saldo(
                                loan_type_account = res.loan_type_account,
                                loan_id = res.loan_id,
                                account_code = res.account_code,
                                coa = res.coa,     
                                code_filial = res.code_filial, 
                                saldo_in = res.saldo_in,  
                                saldo_out = res.saldo_out,  
                                turnover_debit = res.turnover_debit,  
                                turnover_credit = res.turnover_credit,  
                                turnover_all_debit = res.turnover_all_debit,  
                                turnover_all_credit = res.turnover_all_credit,  
                                oper_day = res.oper_day, 
                                created_at = datetime.now())

                    
                    db_session.add(new_account)
                    flush_object(db_session)
        add_oper_day_to_checker(res.oper_day, db_session)
        commit_object(db_session)
    else:
        cron_logger.info(f'for {day} data exists')
    print('finished')
    return 0

def unchek_balance_turnover_update(db_session):
    checker = db_session.query(CheckBalanceTurnoverUpdate).first()
    checker.is_updated_debt_account = False
    checker.is_updated_account_163xx = False
    checker.is_updated_account_95413_9150x = False
    commit_object(db_session)
    
    
def chek_balance_turnover(db_session):
    checker = db_session.query(CheckBalanceTurnoverUpdate).first()
    return checker




@measure_time
def turnover_load_debt_account_16377_start_state_and_repayment_date(db_session):
    today = datetime.now().date()
    checker = chek_balance_turnover(db_session)
    i=0
    if define_is_the_date_holiday_or_weekend(today, db_session) and not checker.is_updated_debt_account:
        get_loans = db_session.query(Loan_Portfolio.loan_id, Loan_Portfolio.overdue_balance, Loan_Portfolio.judicial_balance, Loan_Portfolio.balance_16377)\
            .filter(Loan_Portfolio.status==1).all()      
        for loan in get_loans:
            overdue_balance = 0
            balance_16377 = 0
            juridical_balance = 0
            if loan.overdue_balance is not None:
                overdue_balance = float(loan.overdue_balance)
            if loan.balance_16377 is not None:
                balance_16377 = float(loan.balance_16377)
            if loan.judicial_balance is not None:
                juridical_balance = float(loan.judicial_balance) 
                
            turnover = db_session.query(BalanceTurnover).filter(BalanceTurnover.loan_id == loan.loan_id).first()
            if turnover is None:
                new_turnover = BalanceTurnover(
                    loan_id = loan.loan_id,
                    debt_account_start_state = overdue_balance + juridical_balance,
                    account_16377_start_state = balance_16377,
                    created_at = datetime.now()
                )
                db_session.add(new_turnover)
                flush_object(db_session)
            else:
                turnover.debt_account_start_state = overdue_balance + juridical_balance
                turnover.account_16377_start_state = balance_16377
                turnover.updated_at = datetime.now()
                flush_object(db_session)
            if i%1000==0:
                print(i,'!!')
            i=i+1
        checker.is_updated_debt_account = True
        commit_object(db_session)
        turnover_load_repayment_date(db_session)
        
from fastapi import HTTPException
# @measure_time
# def turnover_163XX_accounts_start_state(db_session):
#     today = datetime.now().date()
#     checker = chek_balance_turnover(db_session)
#     from openpyxl import load_workbook
#     path_to_portfolio = f'project_files/loan_portfolio/29.12.2023.xlsx'
#     i=0
#     try:
#         book = load_workbook(path_to_portfolio, data_only=True, read_only = True, keep_vba = False)
#     except FileNotFoundError  as e:
#         cron_logger.error(e)
#         raise HTTPException(status_code=403, detail=str(e))
#     sheet = book.active
#     rows = sheet.rows
#     start = False
#     for _ in range(0, sheet.max_row):
            
#         strokes = next(rows)
#         if strokes[0].value == 'NN':
#             start = True
#             continue
#         if start:
            
#             if strokes[0].value != None:
#                 balance_16309 = 0
#                 balance_16323 = 0
#                 balance_16325 = 0
#                 balance_16379 = 0
#                 balance_16397 = 0
#                 get_turnover = db_session.query(BalanceTurnover).filter(BalanceTurnover.loan_id == strokes[6].value).first()
#                 if get_turnover is not None:
#                     if strokes[62].value is not None:
#                         balance_16309 = float(strokes[62].value)
#                     if strokes[64].value is not None:
#                         balance_16323 = float(strokes[64].value)
#                     if strokes[65].value is not None:
#                         balance_16325 = float(strokes[65].value)
#                     if strokes[63].value is not None:
#                         balance_16379 = float(strokes[63].value)
#                     if strokes[68].value is not None:
#                         balance_16397 = float(strokes[68].value)
#                     get_turnover.account_163xx_start_state = round(balance_16309+balance_16323+balance_16325+balance_16379+balance_16397,2)
#                     flush_object(db_session)
#     commit_object(db_session)

    # if define_is_the_date_holiday_or_weekend(today, db_session) and not checker.is_updated_account_163xx:
    #     Accountprefixes = db_session.query(AccountPrefix).filter(AccountPrefix.code !='16377').all()
    #     prefixes = [x.code for x in Accountprefixes]
    #     date = datetime.strptime('2023-08-23', '%Y-%m-%d').date()
    #     yesterday = (datetime.now()-timedelta(days=16)).date().strftime("%Y-%m-%d")
    #     cron_logger.info(f'for {yesterday}')
    #     today = datetime.now().date().strftime("%Y-%m-%d")
    #     get_loans = db_session.execute(text(f'''SELECT SALDO.LOAN_ID,
    #                                             -sum(SALDO.SALDO_OUT::BIGINT) as START_16XX
    #                                             FROM LOAN_PORTFOLIO
    #                                             JOIN SALDO ON SALDO.LOAN_ID = LOAN_PORTFOLIO.LOAN_ID
    #                                             WHERE SALDO.COA in {tuple(prefixes)}
    #                                             AND SALDO.OPER_DAY = '{yesterday}'
    #                                             group by SALDO.LOAN_ID
    #                                                 ''') ).fetchall()
        
    #     for loan in get_loans:
            
    #         account_163xx_start_state = 0
    #         get_turnover = db_session.query(BalanceTurnover).filter(BalanceTurnover.loan_id == loan.loan_id).first()
    #         if get_turnover is not None:
    #             if get_turnover.account_163xx_start_state is not None:
    #                 account_163xx_start_state = float(get_turnover.account_163xx_start_state)
                
    #             get_turnover.account_163xx_start_state = round(account_163xx_start_state + float(loan.start_16xx),2)
    #             flush_object(db_session)
    #     checker.is_updated_account_163xx = True
    #     db_session.add(checker)
    #     commit_object(db_session)


# @measure_time
# def turnover_load_account_16377_start_state(db_session):
#     date = (datetime.now()-timedelta(days=14)).date()
#     checker = chek_balance_turnover(db_session)
#     yesterday = date.strftime('%Y-%m-%d')
#     if define_is_the_date_holiday_or_weekend(date, db_session):
        
#         get_loans = db_session.execute(text(f'''SELECT LOAN_PORTFOLIO.LOAN_ID,
#                                                     -(SALDO.SALDO_OUT::BIGINT) AS SALDO_OUT
#                                                     FROM LOAN_PORTFOLIO
#                                                     JOIN SALDO ON SALDO.LOAN_ID = LOAN_PORTFOLIO.LOAN_ID
#                                                     WHERE SALDO.COA = 16377
#                                                     AND SALDO.OPER_DAY = '{yesterday}'
#                                                     ''')).fetchall()
        
#         for loan in get_loans:
#             get_turnover = db_session.query(BalanceTurnover).filter(BalanceTurnover.loan_id == loan.loan_id).first()
#             if get_turnover is not None:
#                 get_turnover.account_16377_start_state = loan.saldo_out/100
#                 db_session.add(get_turnover)
            
            
#             flush_object(db_session)   
#         commit_object(db_session)


@measure_time
def turnover_163XX_accounts_start_state(db_session):
    today = datetime.now().date()
    checker = chek_balance_turnover(db_session)
    i=1
    # loans = db_session.query(Loan_Portfolio).filter(or_(Loan_Portfolio.balance_16309 is not None, \
    #     or_(or_(Loan_Portfolio.balance_16323 is not None, Loan_Portfolio.balance_16325 is not None), \
    #     or_(Loan_Portfolio.balance_16379 is not None, Loan_Portfolio.balance_16397 is not None)))).count()
    if define_is_the_date_holiday_or_weekend(today, db_session) and not checker.is_updated_account_163xx:
        loans = db_session.execute(text(f'''select loan_id, balance_16309, balance_16323, balance_16325, balance_16379, balance_16397 from loan_portfolio
                                            where (balance_16309 is not null
                                                or balance_16323 is not null
                                                or balance_16325 is not null
                                                or balance_16379 is not null
                                                or balance_16397 is not null)
                                                and status=1
                                                
                                                        ''')).fetchall()
        
        
        for loan in loans:
            if i%10000==0:
                print(i)
            i=i+1
            balance_16309 = 0
            balance_16323 = 0
            balance_16325 = 0
            balance_16379 = 0
            balance_16397 = 0
            get_turnover = db_session.query(BalanceTurnover).filter(BalanceTurnover.loan_id == loan.loan_id).first()
            if get_turnover is not None:
                if loan.balance_16309 is not None:
                    balance_16309 = float(loan.balance_16309)
                if loan.balance_16323 is not None:
                    balance_16323 = float(loan.balance_16323)
                if loan.balance_16325 is not None:
                    balance_16325 = float(loan.balance_16325)
                if loan.balance_16379 is not None:
                    balance_16379 = float(loan.balance_16379)
                if loan.balance_16397 is not None:
                    balance_16397 = float(loan.balance_16397)
                get_turnover.account_163xx_start_state = round(balance_16309+balance_16323+balance_16325+balance_16379+balance_16397,2)
                flush_object(db_session)
        checker.is_updated_account_163xx = True
        commit_object(db_session)


@measure_time
def turnover_load_repayment_date(db_session):
    today = datetime.now().date()
    all_duty = case([
        (and_(Loan_Portfolio.overdue_balance != None, Loan_Portfolio.balance_16377 != None), 
         cast(Loan_Portfolio.overdue_balance, sqlalchemy.FLOAT) + cast(Loan_Portfolio.balance_16377, sqlalchemy.FLOAT)),
        (and_(Loan_Portfolio.overdue_balance != None, Loan_Portfolio.balance_16377 == None), 
         cast(Loan_Portfolio.overdue_balance, sqlalchemy.FLOAT)),
        (and_(Loan_Portfolio.overdue_balance == None, Loan_Portfolio.balance_16377 != None), 
         cast(Loan_Portfolio.balance_16377, sqlalchemy.FLOAT)),
        ], else_=None).label('all_duty')
    schedule_sum = case([(func.sum(cast(LoanPortfolioSchedule.summ_red, sqlalchemy.FLOAT))==None, 0)], else_=func.sum(cast(LoanPortfolioSchedule.summ_red, sqlalchemy.FLOAT))).label('schedule_sum')
    
    sub_query_schedule_sum = db_session.query(schedule_sum).filter(Loan_Portfolio.loan_id==LoanPortfolioSchedule.loan_id).filter(Loan_Portfolio.status==1)\
        .filter(LoanPortfolioSchedule.date_red>=datetime.now()).scalar_subquery().correlate(Loan_Portfolio)
    
    get_schedules = db_session.query(LoanPortfolioSchedule.loan_id,
                                     LoanPortfolioSchedule.summ_red,
                                     all_duty,
                                     Loan_Portfolio.currency_id,
                                     Loan_Portfolio.overdue_balance,
                                     Loan_Portfolio.total_overdue,
                                     Loan_Portfolio.balance_16377,
                                     sub_query_schedule_sum.label('total_overdue_by_graph'),
                                     LoanPortfolioSchedule.date_red)\
        .join(Loan_Portfolio, Loan_Portfolio.loan_id == LoanPortfolioSchedule.loan_id, isouter=True)\
        .filter(extract('month', LoanPortfolioSchedule.date_red) == today.month)\
            .filter(extract('year', LoanPortfolioSchedule.date_red) ==today.year)\
                .filter(Loan_Portfolio.status==1).all()
    get_currency_rate = db_session.query(CurrencyRate.code, CurrencyRate.equival).filter(CurrencyRate.date == datetime.now().date()).all()
    curr_rates = {}
    for dir in get_currency_rate:
        curr_rates[dir.code] = dir.equival
    print(curr_rates)
    for schedule in get_schedules:
        recommended_amount = schedule.summ_red and float(schedule.summ_red) or 0
        total_overdue = 0
        total_overdue_by_graph = 0
        if schedule.summ_red is not None:
            recommended_amount = float(schedule.summ_red)
        if schedule.total_overdue is not None and schedule.total_overdue !='0':
            total_overdue= schedule.total_overdue
        if schedule.total_overdue_by_graph is not None and schedule.total_overdue_by_graph!=0:
            total_overdue_by_graph = schedule.total_overdue_by_graph/100
            
        if float(total_overdue) < total_overdue_by_graph:
            recommended_amount = 0
        if (schedule.all_duty == 0 or schedule.all_duty is None) and recommended_amount == 0:
            continue
        
        turnover = db_session.query(BalanceTurnover).filter(BalanceTurnover.loan_id == schedule.loan_id).first()
        if turnover is not None:
            turnover.lead_last_date = schedule.date_red
            if schedule.currency_id==122:
                recommended_amount = recommended_amount * curr_rates[schedule.currency_id]
            if schedule.currency_id==90:
                recommended_amount = recommended_amount * curr_rates[schedule.currency_id]
            turnover.debt_account_start_state = float(turnover.debt_account_start_state) + round(recommended_amount/100,2)
            flush_object(db_session)
            
    commit_object(db_session)


@measure_time
def turnover_main_accounts_credit_sums(db_session, day=None):
    if day is None:
        day=1
    yesterday = (datetime.now()-timedelta(days=day)).date().strftime("%Y-%m-%d")
    checker = check_oper_day_update(yesterday, db_session)
    if not checker.is_updated_main_accounts_credit_sums:
        cron_logger.info(f'for {yesterday}')
        get_loans = db_session.execute(text(f'''SELECT LOAN_PORTFOLIO.DEBT_ACCOUNT,
                                                LOAN_PORTFOLIO.LOAN_ID,
                                                LOAN_PORTFOLIO.CURRENCY_ID,
                                                SALDO.TURNOVER_DEBIT,
                                                SALDO.TURNOVER_CREDIT
                                                FROM LOAN_PORTFOLIO
                                                JOIN SALDO ON SALDO.LOAN_ID = LOAN_PORTFOLIO.LOAN_ID
                                                WHERE SALDO.COA::TEXT in (substring(LOAN_PORTFOLIO.DEBT_ACCOUNT, 1,5), substring(LOAN_PORTFOLIO.JUDICIAL_ACCOUNT, 1,5), BALANCE_ACCOUNT)
                                                AND SALDO.OPER_DAY = '{yesterday}'
                                                AND LOAN_PORTFOLIO.STATUS=1
                                                    ''')).fetchall()
        get_currency_rate = db_session.query(CurrencyRate.code, CurrencyRate.equival).filter(CurrencyRate.date == datetime.now().date()).all()
        curr_rates = {}
        for dir in get_currency_rate:
                curr_rates[dir.code] = dir.equival
        for loan in get_loans:
            debt_account_credit_sum = 0
            get_turnover = db_session.query(BalanceTurnover).filter(BalanceTurnover.loan_id == loan.loan_id).first()
            if get_turnover is not None:
                
                turnover_credit = float(loan.turnover_credit)
                turnover_debit = float(loan.turnover_debit)
                
                if get_turnover.debt_account_credit_sum is not None:
                    debt_account_credit_sum = float(get_turnover.debt_account_credit_sum)
                if loan.currency_id==122:
                    turnover_credit = turnover_credit * curr_rates[loan.currency_id]
                    turnover_debit = turnover_debit * curr_rates[loan.currency_id]
                if loan.currency_id==90:
                    turnover_credit = turnover_credit * curr_rates[loan.currency_id]
                    turnover_debit = turnover_debit * curr_rates[loan.currency_id]
                get_turnover.debt_account_credit_sum = round(debt_account_credit_sum + turnover_credit - turnover_debit,2)
                db_session.add(get_turnover)
            flush_object(db_session)
        checker.is_updated_main_accounts_credit_sums = True
    commit_object(db_session)
    return "OK"
    
    
    
    

@measure_time
def turnover_16377_accounts_credit_debit_sums(db_session, day=None):
    if day is None:
        day=1
    # Accountprefixes = db_session.query(AccountPrefix).filter(AccountPrefix.code !='16377').all()
    #date = datetime.strptime('2023-08-23', '%Y-%m-%d').date()
    date = datetime.today().date().strftime('%Y-%m-%d')
    yesterday = (datetime.now()-timedelta(days=day)).date().strftime("%Y-%m-%d")
    checker = check_oper_day_update(yesterday, db_session)
    if not checker.is_updated_16377_accounts_credit_debit_sums:
        cron_logger.info(f'for {yesterday}')
        get_loans = db_session.execute(text(f'''SELECT LOAN_PORTFOLIO.LOAN_ID,
                                                    LOAN_PORTFOLIO.CURRENCY_ID,
                                                    SALDO.TURNOVER_CREDIT,
                                                    SALDO.TURNOVER_DEBIT
                                                    FROM LOAN_PORTFOLIO
                                                    JOIN SALDO ON SALDO.LOAN_ID = LOAN_PORTFOLIO.LOAN_ID
                                                    WHERE SALDO.COA = 16377
                                                    AND SALDO.OPER_DAY = '{yesterday}'
                                                    ''')).fetchall()
        get_currency_rate = db_session.query(CurrencyRate.code, CurrencyRate.equival).filter(CurrencyRate.date == datetime.now().date()).all()
        curr_rates = {}
        for dir in get_currency_rate:
                curr_rates[dir.code] = dir.equival
        for loan in get_loans:
            account_16377_debit_sum = 0
            account_16377_credit_sum = 0
            get_turnover = db_session.query(BalanceTurnover).filter(BalanceTurnover.loan_id == loan.loan_id).first()
            if get_turnover is not None:
                
                turnover_credit = float(loan.turnover_credit)
                turnover_debit = float(loan.turnover_debit)
                
                if get_turnover.account_16377_debit_sum is not None:
                    account_16377_debit_sum = float(get_turnover.account_16377_debit_sum)
                if get_turnover.account_16377_credit_sum is not None:
                    account_16377_credit_sum = float(get_turnover.account_16377_credit_sum)
                if loan.currency_id==122:
                    turnover_credit = turnover_credit * curr_rates[loan.currency_id]
                    turnover_debit = turnover_debit * curr_rates[loan.currency_id]
                if loan.currency_id==90:
                    turnover_credit = turnover_credit * curr_rates[loan.currency_id]
                    turnover_debit = turnover_debit * curr_rates[loan.currency_id]
                get_turnover.account_16377_debit_sum = round(account_16377_debit_sum + turnover_debit,2)
                get_turnover.account_16377_credit_sum = round(account_16377_credit_sum + turnover_credit,2)
                db_session.add(get_turnover)
            flush_object(db_session)
        checker.is_updated_16377_accounts_credit_debit_sums = True
    commit_object(db_session)
    
    

@measure_time
def turnover_163XX_accounts_credit_debit_sums(db_session, day=None):
    if day is None:
        day=1
    yesterday = (datetime.now()-timedelta(days=day)).date().strftime("%Y-%m-%d")
    Accountprefixes = db_session.query(AccountPrefix).filter(AccountPrefix.code !='16377').all()
    prefixes = [x.code for x in Accountprefixes]
    checker = check_oper_day_update(yesterday, db_session)
    if not checker.is_updated_163xx_accounts_credit_debit_sums:
        cron_logger.info(f'for {yesterday}')
        get_loans = db_session.execute(text(f'''SELECT SALDO.LOAN_ID,
                                                LOAN_PORTFOLIO.CURRENCY_ID,
                                                SUM(SALDO.TURNOVER_CREDIT::BIGINT) AS CREDIT_16XX,
                                                SUM(SALDO.TURNOVER_DEBIT::BIGINT) AS DEBIT_16XX
                                                FROM LOAN_PORTFOLIO
                                                JOIN SALDO ON SALDO.LOAN_ID = LOAN_PORTFOLIO.LOAN_ID
                                                WHERE SALDO.COA in {tuple(prefixes)}
                                                AND SALDO.OPER_DAY = '{yesterday}'
                                                group by SALDO.LOAN_ID, LOAN_PORTFOLIO.CURRENCY_ID
                                                    ''')).fetchall()
        get_currency_rate = db_session.query(CurrencyRate.code, CurrencyRate.equival).filter(CurrencyRate.date == datetime.now().date()).all()
        curr_rates = {}
        for dir in get_currency_rate:
                curr_rates[dir.code] = dir.equival                                                                                                                                                                
        for loan in get_loans:
            account_163xx_debit_sum = 0
            account_163xx_credit_sum = 0
            get_turnover = db_session.query(BalanceTurnover).filter(BalanceTurnover.loan_id == loan.loan_id).first()
            if get_turnover is not None:
                
                credit_16xx = float(loan.credit_16xx)
                debit_16xx = float(loan.debit_16xx)
                
                if get_turnover.account_163xx_debit_sum is not None:
                    account_163xx_debit_sum = float(get_turnover.account_163xx_debit_sum)
                if get_turnover.account_163xx_credit_sum is not None:
                    account_163xx_credit_sum = float(get_turnover.account_163xx_credit_sum)
                if loan.currency_id==122:
                    credit_16xx = credit_16xx * curr_rates[loan.currency_id]
                    debit_16xx = debit_16xx * curr_rates[loan.currency_id]
                if loan.currency_id==90:
                    credit_16xx = credit_16xx * curr_rates[loan.currency_id]
                    debit_16xx = debit_16xx * curr_rates[loan.currency_id]
                get_turnover.account_163xx_debit_sum = round(account_163xx_debit_sum + debit_16xx,2)
                get_turnover.account_163xx_credit_sum = round(account_163xx_credit_sum + credit_16xx,2)
                
            flush_object(db_session)
        checker.is_updated_163xx_accounts_credit_debit_sums = True
    commit_object(db_session)



#1. выгрузить портфель за последний рабочий день месяца
#2. перенести данные в архив
#3. загрузить графики новых кредитов 
#4. делать фиксировку
#. выгрузить портфель за 1ое число
#5. делать суммировки
def  export_balance_turnover_data_to_history(db_session):
    period = date (datetime.today().year, datetime.today().month, 1) - timedelta (days = 1)
    while define_is_the_date_holiday_or_weekend(period, db_session) is False:
        period = period - timedelta (days = 1)
        print(period)
    db_session.execute(text(f'''insert into balance_turnover_history (loan_id, debt_account_start_state, debt_account_credit_sum, account_16377_start_state,
                                        account_16377_debit_sum, account_16377_credit_sum, account_163XX_start_state, account_163XX_debit_sum,
                                        account_163XX_credit_sum, period)
                                    select loan_id, debt_account_start_state, debt_account_credit_sum, account_16377_start_state,
                                        account_16377_debit_sum, account_16377_credit_sum, account_163xx_start_state, account_163xx_debit_sum,
                                        account_163xx_credit_sum, '{period}' as period from balance_turnover
                                                '''))
    db_session.execute( '''TRUNCATE TABLE balance_turnover''' )
    db_session.execute("ALTER SEQUENCE balance_turnover_id_seq RESTART WITH 1")
    commit_object(db_session)
    return 'OK'


def get_last_oper_day(db_session):
    return db_session.query(CheckBalanceTurnoverUpdatePerOperDay.oper_day).order_by(CheckBalanceTurnoverUpdatePerOperDay.oper_day.desc()).first()

def get_last_portfolio_day(db_session):
    return db_session.query(Loan_Portfolio_Date.date).order_by(Loan_Portfolio_Date.date.desc()).first()

def check_oper_day_update(oper_day, db_session):
    check = db_session.query(CheckBalanceTurnoverUpdatePerOperDay).filter(CheckBalanceTurnoverUpdatePerOperDay.oper_day == oper_day).first()
    is_exists(check, 400, f'accounts are not loaded for the current {oper_day} operating day')
    return check

def add_oper_day_to_checker(oper_day, db_session):
    check = db_session.query(CheckBalanceTurnoverUpdatePerOperDay).filter(CheckBalanceTurnoverUpdatePerOperDay.oper_day == oper_day).first()
    is_empty(check, 400, f'accounts are not loaded for the current {oper_day} operating day')
    new_oper_day_to_checker = CheckBalanceTurnoverUpdatePerOperDay(oper_day = oper_day)
    db_session.add(new_oper_day_to_checker)
    flush_object(db_session)
    return 'OK'


def all_turnover_account_update(db_session):
    get_dates = db_session.query(CheckBalanceTurnoverUpdatePerOperDay).filter(CheckBalanceTurnoverUpdatePerOperDay.is_updated_main_accounts_credit_sums ==False).all()
    
    for date in get_dates:
        diff = (datetime.now().date() - date.oper_day).days
    
        turnover_main_accounts_credit_sums(db_session, diff)
        turnover_16377_accounts_credit_debit_sums(db_session, diff)
        turnover_163XX_accounts_credit_debit_sums(db_session, diff)
        turnover_95413_accounts_credit_debit_sums(db_session, diff)
        turnover_9150x_accounts_credit_debit_sums(db_session, diff)
    #!
    return "OK"


@measure_time
def turnover_95413_and_9150x_accounts_start_state(db_session):
    today = datetime.now().date()
    checker = chek_balance_turnover(db_session)
    # loans = db_session.query(Loan_Portfolio).filter(or_(Loan_Portfolio.balance_16309 is not None, \
    #     or_(or_(Loan_Portfolio.balance_16323 is not None, Loan_Portfolio.balance_16325 is not None), \
    #     or_(Loan_Portfolio.balance_16379 is not None, Loan_Portfolio.balance_16397 is not None)))).count()
    if define_is_the_date_holiday_or_weekend(today, db_session) and not checker.is_updated_account_95413_9150x:
        loans = db_session.execute(text(f'''select loan_id, balance_95413, balance_91501, balance_91503 from loan_portfolio
                                            where balance_95413 is not null
                                                or balance_91501 is not null
                                                or balance_91503 is not null
                                                        ''')).fetchall()
        for loan in loans:
            balance_95413 = 0
            balance_91501 = 0
            balance_91503 = 0
            get_turnover = db_session.query(BalanceTurnover).filter(BalanceTurnover.loan_id == loan.loan_id).first()
            if get_turnover is not None:
                if loan.balance_95413 is not None:
                    balance_95413 = float(loan.balance_95413)
                if loan.balance_91501 is not None:
                    balance_91501 = float(loan.balance_91501)
                if loan.balance_91503 is not None:
                    balance_91503 = float(loan.balance_91503)
                get_turnover.account_95413_start_state = round(balance_95413,2)
                get_turnover.account_9150x_start_state = round(balance_91501 + balance_91503,2)
                flush_object(db_session)
        checker.is_updated_account_95413_9150x = True
        commit_object(db_session)


@measure_time
def turnover_95413_accounts_credit_debit_sums(db_session, day=None):
    if day is None:
        day=1
    # Accountprefixes = db_session.query(AccountPrefix).filter(AccountPrefix.code !='16377').all()
    #date = datetime.strptime('2023-08-23', '%Y-%m-%d').date()
    date = datetime.today().date().strftime('%Y-%m-%d')
    yesterday = (datetime.now()-timedelta(days=day)).date().strftime("%Y-%m-%d")
    checker = check_oper_day_update(yesterday, db_session)
    if not checker.is_updated_95413_accounts_credit_debit_sums:
        cron_logger.info(f'for {yesterday}')
        get_loans = db_session.execute(text(f'''SELECT LOAN_PORTFOLIO.LOAN_ID,
                                                    LOAN_PORTFOLIO.CURRENCY_ID,
                                                    SALDO.TURNOVER_CREDIT,
                                                    SALDO.TURNOVER_DEBIT
                                                    FROM LOAN_PORTFOLIO
                                                    JOIN SALDO ON SALDO.LOAN_ID = LOAN_PORTFOLIO.LOAN_ID
                                                    WHERE SALDO.COA = 95413
                                                    AND SALDO.OPER_DAY = '{yesterday}'
                                                    ''')).fetchall()
        get_currency_rate = db_session.query(CurrencyRate.code, CurrencyRate.equival).filter(CurrencyRate.date == datetime.now().date()).all()
        curr_rates = {}
        for dir in get_currency_rate:
                curr_rates[dir.code] = dir.equival 
        for loan in get_loans:
            account_95413_debit_sum = 0
            account_95413_credit_sum = 0
            get_turnover = db_session.query(BalanceTurnover).filter(BalanceTurnover.loan_id == loan.loan_id).first()
            if get_turnover is not None:
                
                turnover_credit = float(loan.turnover_credit)
                turnover_debit = float(loan.turnover_debit)
                
                if get_turnover.account_95413_debit_sum is not None:
                    account_95413_debit_sum = float(get_turnover.account_95413_debit_sum)
                if get_turnover.account_95413_credit_sum is not None:
                    account_95413_credit_sum = float(get_turnover.account_95413_credit_sum)
                if loan.currency_id==122:
                    turnover_credit = turnover_credit * curr_rates[loan.currency_id]
                    turnover_debit = turnover_debit * curr_rates[loan.currency_id]
                if loan.currency_id==90:
                    turnover_credit = turnover_credit * curr_rates[loan.currency_id]
                    turnover_debit = turnover_debit * curr_rates[loan.currency_id]
                get_turnover.account_95413_debit_sum = round(account_95413_debit_sum + turnover_debit,2)
                get_turnover.account_95413_credit_sum = round(account_95413_credit_sum + turnover_credit,2)
                db_session.add(get_turnover)
            flush_object(db_session)
        checker.is_updated_95413_accounts_credit_debit_sums = True
    commit_object(db_session)


@measure_time
def turnover_9150x_accounts_credit_debit_sums(db_session, day=None):
    if day is None:
        day=1
    yesterday = (datetime.now()-timedelta(days=day)).date().strftime("%Y-%m-%d")
    Accountprefixes = db_session.query(AccountPrefix).filter(or_(AccountPrefix.code == '91501', AccountPrefix.code =='91503')).all()
    prefixes = [x.code for x in Accountprefixes]
    checker = check_oper_day_update(yesterday, db_session)
    if not checker.is_updated_9150x_accounts_credit_debit_sums:
        cron_logger.info(f'for {yesterday}')
        get_loans = db_session.execute(text(f'''SELECT SALDO.LOAN_ID,
                                                LOAN_PORTFOLIO.CURRENCY_ID,
                                                SUM(SALDO.TURNOVER_CREDIT::BIGINT) AS CREDIT_9150X,
                                                SUM(SALDO.TURNOVER_DEBIT::BIGINT) AS DEBIT_9150X
                                                FROM LOAN_PORTFOLIO 
                                                JOIN SALDO ON SALDO.LOAN_ID = LOAN_PORTFOLIO.LOAN_ID
                                                WHERE SALDO.COA in {tuple(prefixes)}
                                                AND SALDO.OPER_DAY = '{yesterday}'
                                                group by SALDO.LOAN_ID, LOAN_PORTFOLIO.CURRENCY_ID
                                                    ''')).fetchall()
        get_currency_rate = db_session.query(CurrencyRate.code, CurrencyRate.equival).filter(CurrencyRate.date == datetime.now().date()).all()
        curr_rates = {}
        for dir in get_currency_rate:
                curr_rates[dir.code] = dir.equival                                                                                                                                                                 
        for loan in get_loans:
            account_9150x_debit_sum = 0
            account_9150x_credit_sum = 0
            get_turnover = db_session.query(BalanceTurnover).filter(BalanceTurnover.loan_id == loan.loan_id).first()
            if get_turnover is not None:
                
                credit_9150x = float(loan.credit_9150x)
                debit_9150x = float(loan.debit_9150x)
                
                if get_turnover.account_9150x_debit_sum is not None:
                    account_9150x_debit_sum = float(get_turnover.account_9150x_debit_sum)
                if get_turnover.account_9150x_credit_sum is not None:
                    account_9150x_credit_sum = float(get_turnover.account_9150x_credit_sum)
                    
                if loan.currency_id==122:
                    credit_9150x = credit_9150x * curr_rates[loan.currency_id]
                    debit_9150x = debit_9150x * curr_rates[loan.currency_id]
                if loan.currency_id==90:
                    credit_9150x = credit_9150x * curr_rates[loan.currency_id]
                    debit_9150x = debit_9150x * curr_rates[loan.currency_id]
                    
                get_turnover.account_9150x_debit_sum = round(account_9150x_debit_sum + debit_9150x,2)
                get_turnover.account_9150x_credit_sum = round(account_9150x_credit_sum + credit_9150x,2)
                
            flush_object(db_session)
        checker.is_updated_9150x_accounts_credit_debit_sums = True
    commit_object(db_session)