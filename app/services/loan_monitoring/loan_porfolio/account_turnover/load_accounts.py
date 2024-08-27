from datetime import datetime, timedelta
from sqlalchemy.sql import text

from app.config.logs_config import cron_logger
from .....models.brief_case.loan_portfolio import Loan_Portfolio
from .....models.balance_turnover.balance_turnover_model import Saldo, CheckBalanceTurnoverUpdatePerOperDay
from .....models.balance_turnover.account_prefix_model import AccountPrefix
from .....common.commit import commit_object, flush_object
from .....common.is_empty import is_empty
from app.db.connect_db import SessionManager
from app.db.oracle_connect import OracleSessionManager
import argparse



def load_all_accounts(day:int=None):
    with OracleSessionManager() as orc_session:
        with SessionManager() as db_session:
            p_size = 1000
            page = 1
            count_none = 0
            exist_day = None
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
                    if result !=[]:
                        exist_day = today
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
                    else:
                        count_none+=1
                    if count_none > 10:
                        print('empty data')
                        return 0
                if exist_day is not None:
                    add_oper_day_to_checker(res.oper_day, db_session)
                commit_object(db_session)
            else:
                cron_logger.info(f'for {day} data exists')
            print('finished')
            return 0












def add_oper_day_to_checker(oper_day, db_session):
    check = db_session.query(CheckBalanceTurnoverUpdatePerOperDay).filter(CheckBalanceTurnoverUpdatePerOperDay.oper_day == oper_day).first()
    is_empty(check, 400, f'accounts are not loaded for the current {oper_day} operating day')
    new_oper_day_to_checker = CheckBalanceTurnoverUpdatePerOperDay(oper_day = oper_day)
    db_session.add(new_oper_day_to_checker)
    flush_object(db_session)
    return 'OK'







def test():
    return 0





if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Описание вашего скрипта")
    parser.add_argument("--days", type=str, required=True, help="Описание param1")
    args = parser.parse_args()
    print(args.days)
    for day in reversed(range(2, int(args.days)+1)):
       load_all_accounts(day)