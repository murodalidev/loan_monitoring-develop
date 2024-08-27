import datetime
from sqlalchemy import or_, and_
import sqlalchemy
from sqlalchemy.sql import text
from sqlalchemy.sql.expression import cast, extract
from app.models.loan_case.loan_case_model import LoanCase
from app.models.problems_case.problem_state_chain_model import ProblemStateChain
from app.models.problems_case.problem_states_model import ProblemStates
from ...models.kad_case.kad_case_model import KADCase
from app.models.brief_case.directories.currency import currency
from ...models.business_case.business_case_model import BusinessCase
from ...models.brief_case.loan_portfolio import Loan_Portfolio
from ...models.balance_turnover.balance_turnover_model import BalanceTurnover
from ...models.monitoring_task_manager.task_manager_model import TaskManager
from ...models.users.users import Users as users_model
from ...models.brief_case.directories.loan_product import loan_product
from ...common.commit import flush_object
from ...models.brief_case.directories.bank_mfo import bank_mfo
from ...models.brief_case.directories.local_code import local_code
from ...models.statuses.business_case_status_model import BusinessCaseStatus
from ...common.dictionaries.monitoring_case_dictionary import loan_case
from ...common.dictionaries.from_type import FromType
from ...common.dictionaries.general_tasks_dictionary import KGT
from sqlalchemy.orm import aliased
from sqlalchemy import case
from ...models.brief_case.loan_portfolio_schedule import LoanPortfolioSchedule
from calendar import monthrange



def get_kad_all_turnover(size, page, user, region_id,local_code_id,client_name, currency_id, loan_id, state_chain, product_type, main_responsible, second_responsible, client_type, db_session):
    user_roles = []
    for role in user.roles:
        user_roles.append(role.name)
    debt_account_start_state = case(
                        [
                            (BalanceTurnover.debt_account_start_state != None, cast(BalanceTurnover.debt_account_start_state, sqlalchemy.FLOAT))
                        ], else_=0).label("debt_account_start_state")
    account_16377_start_state = case(
                        [
                            (BalanceTurnover.account_16377_start_state != None, cast(BalanceTurnover.account_16377_start_state, sqlalchemy.FLOAT))
                        ], else_=0).label("account_16377_start_state")
    account_163xx_start_state = case(
                        [
                            (BalanceTurnover.account_163xx_start_state != None, cast(BalanceTurnover.account_163xx_start_state, sqlalchemy.FLOAT))
                        ], else_=0).label("account_163xx_start_state")
    
    
    debt_account_credit_sum = case(
                        [
                            (BalanceTurnover.debt_account_credit_sum != None, cast(BalanceTurnover.debt_account_credit_sum, sqlalchemy.FLOAT)/100)
                        ], else_=0).label("debt_account_credit_sum")
    
    account_16377_debit_sum = case(
                        [
                            (BalanceTurnover.account_16377_debit_sum != None, cast(BalanceTurnover.account_16377_debit_sum, sqlalchemy.FLOAT)/100)
                        ], else_=0).label("account_16377_debit_sum")
    account_16377_credit_sum = case(
                        [
                            (BalanceTurnover.account_16377_credit_sum != None, cast(BalanceTurnover.account_16377_credit_sum, sqlalchemy.FLOAT)/100)
                        ], else_=0).label("account_16377_credit_sum")
    
    account_163xx_debit_sum = case(
                        [
                            (BalanceTurnover.account_163xx_debit_sum != None, cast(BalanceTurnover.account_163xx_debit_sum, sqlalchemy.FLOAT)/100)
                        ], else_=0).label("account_163xx_debit_sum")
    account_163xx_credit_sum = case(
                        [
                            (BalanceTurnover.account_163xx_credit_sum != None, cast(BalanceTurnover.account_163xx_credit_sum, sqlalchemy.FLOAT)/100)
                        ], else_=0).label("account_163xx_credit_sum")
    
    current_date = datetime.datetime.now().date()
    get_turnover = db_session.query(Loan_Portfolio.id,
                                    KADCase.id.label('kad_id'),
                                    LoanCase.monitoring_case_id.label("monitoring_case_id"),
                                    KADCase.main_responsible_id.label('main_responsible_id'),
                                    KADCase.second_responsible_id.label('second_responsible_id'),
                                    ProblemStates.name.label('state_chain_name'),
                                    local_code.code,
                                    currency.code.label('currency_code'),
                                    Loan_Portfolio.loan_id,
                                    Loan_Portfolio.client_name,
                                    debt_account_start_state,
                                    debt_account_credit_sum, 
                                    account_16377_start_state, 
                                    account_16377_debit_sum,
                                    account_16377_credit_sum,
                                    account_163xx_start_state,
                                    account_163xx_debit_sum,
                                    account_163xx_credit_sum,
                                    BalanceTurnover.lead_last_date)\
                        .join(Loan_Portfolio, Loan_Portfolio.id == KADCase.loan_portfolio_id, isouter=False)\
                        .join(LoanCase, LoanCase.loan_portfolio_id == KADCase.loan_portfolio_id)\
                        .join(BalanceTurnover, Loan_Portfolio.loan_id == BalanceTurnover.loan_id, isouter=True)\
                            .join(ProblemStateChain, ProblemStateChain.loan_id == Loan_Portfolio.loan_id, isouter = True)\
                            .join(ProblemStates, ProblemStates.id == ProblemStateChain.last_state_id, isouter = True)\
                            .join(local_code, local_code.id == Loan_Portfolio.local_code_id)\
                                .join(currency, Loan_Portfolio.currency_id==currency.id)\
                                .where(or_(and_(Loan_Portfolio.date_overdue_percent== None, Loan_Portfolio.overdue_start_date != None, (current_date-Loan_Portfolio.overdue_start_date)>=31, (current_date-Loan_Portfolio.overdue_start_date)<61), 
and_(Loan_Portfolio.overdue_start_date == None, Loan_Portfolio.date_overdue_percent != None, (current_date-Loan_Portfolio.date_overdue_percent)>=31, (current_date-Loan_Portfolio.date_overdue_percent)<61),
and_(Loan_Portfolio.date_overdue_percent != None, Loan_Portfolio.overdue_start_date != None, Loan_Portfolio.overdue_start_date < Loan_Portfolio.date_overdue_percent, (current_date-Loan_Portfolio.overdue_start_date)>=31, (current_date-Loan_Portfolio.overdue_start_date)<61),
and_(Loan_Portfolio.date_overdue_percent != None, Loan_Portfolio.overdue_start_date != None, Loan_Portfolio.overdue_start_date >= Loan_Portfolio.date_overdue_percent, (current_date-Loan_Portfolio.date_overdue_percent)>=31, (current_date-Loan_Portfolio.date_overdue_percent)<61)))\
    .where(or_(and_(BalanceTurnover.debt_account_start_state!=None, BalanceTurnover.debt_account_start_state!=0),
                and_(BalanceTurnover.debt_account_credit_sum!=None, BalanceTurnover.debt_account_credit_sum!=0),
                and_(BalanceTurnover.account_16377_start_state!=None, BalanceTurnover.account_16377_start_state!=0),
                and_(BalanceTurnover.account_16377_debit_sum!=None, BalanceTurnover.account_16377_debit_sum!=0),
                and_(BalanceTurnover.account_16377_credit_sum!=None, BalanceTurnover.account_16377_credit_sum!=0),
                and_(BalanceTurnover.account_163xx_start_state!=None, BalanceTurnover.account_163xx_start_state!=0),
                and_(BalanceTurnover.account_163xx_debit_sum!=None, BalanceTurnover.account_163xx_debit_sum!=0),
                and_(BalanceTurnover.account_163xx_credit_sum!=None, BalanceTurnover.account_163xx_credit_sum!=0)))\
                    .where(Loan_Portfolio.status == 1)\
                                    
    
    if region_id is not None:
        get_turnover = get_turnover.filter(Loan_Portfolio.client_region == region_id)
    
    
    if 'superviser' in user_roles:
        local_code_id = user.local_code
        
    if 'kad_block_filial_user' in user_roles:
        get_turnover = get_turnover.filter(KADCase.second_responsible_id == user.id)
        
    if 'kad_block_filial_admin' in user_roles:
        get_turnover = get_turnover.filter(KADCase.second_responsible_id == user.id)
        
    if 'kad_block_main_admin' in user_roles:
        get_turnover = get_turnover.filter(KADCase.main_responsible_id == user.id)
    
    if local_code_id is not None:
        get_turnover = get_turnover.filter(Loan_Portfolio.local_code_id == local_code_id)
            
    if main_responsible is not None:
        if 'main_superviser' in user_roles or 'main_superviser_kad' in user_roles or 'main_superviser_kad_with_pledge' in user_roles:
            get_turnover = get_turnover.filter(KADCase.main_responsible_id == main_responsible)
    
    
    if second_responsible is not None:
        get_turnover = get_turnover.filter(KADCase.second_responsible_id == second_responsible)
    
    # if 'superviser' in user_roles:
    #     get_turnover = get_turnover.filter(Loan_Portfolio.local_code_id == user.local_code)
    # else:
    #     get_turnover = get_turnover.filter(KADCase.main_responsible_id==user.id)\
    
    if currency_id is not None:
        get_turnover = get_turnover.filter(Loan_Portfolio.currency_id == currency_id)
    
    if state_chain is not None:
        get_turnover = get_turnover.filter(ProblemStates.id == state_chain)
    
    
    if loan_id is not None or client_name is not None:
        get_turnover = get_turnover.filter(or_(cast(Loan_Portfolio.loan_id, sqlalchemy.Text).like(f'{loan_id}%'), Loan_Portfolio.client_name.ilike(f'%{client_name}%')))
    
    if product_type is not None:
        get_turnover = get_turnover.join(loan_product, loan_product.name == Loan_Portfolio.loan_product)\
        .filter(loan_product.type == product_type) 
    
    if client_type is not None:    
        if client_type != '11' and client_type != '08':
            get_turnover = get_turnover.filter(Loan_Portfolio.borrower_type.regexp_match('^(?!08|11).*'))
        else:
            get_turnover = get_turnover.filter(Loan_Portfolio.borrower_type.regexp_match(f'^({client_type}).*'))
    count = get_turnover.count()
    
    get_turnover = get_turnover.limit(size).offset((page-1)*size).all()
    turnovers = []
    for loan in get_turnover:
        loan_client = loan.loan_id
        if loan.client_name is not None:
            loan_client = str(loan.loan_id) +' : '+ loan.client_name
        debt_account_start_state =0
        if loan.debt_account_start_state is not None:
            debt_account_start_state = loan.debt_account_start_state
        debt_account_credit_sum = 0
        if loan.debt_account_credit_sum is not None:
            debt_account_credit_sum = loan.debt_account_credit_sum
        account_16377_start_state = 0
        if loan.account_16377_start_state is not None:
           account_16377_start_state = loan.account_16377_start_state    
        account_16377_debit_sum = 0
        if loan.account_16377_debit_sum is not None:
            account_16377_debit_sum = loan.account_16377_debit_sum
        account_16377_credit_sum = 0
        if loan.account_16377_credit_sum is not None:
            account_16377_credit_sum = loan.account_16377_credit_sum
        account_163xx_start_state = 0
        if loan.account_163xx_start_state is not None:
            account_163xx_start_state = loan.account_163xx_start_state
        account_163xx_debit_sum = 0
        if loan.account_163xx_debit_sum is not None:
            account_163xx_debit_sum = loan.account_163xx_debit_sum
        account_163xx_credit_sum = 0
        if loan.account_163xx_credit_sum is not None:
            account_163xx_credit_sum = loan.account_163xx_credit_sum
        debt_account_balance = 0
        if debt_account_start_state > debt_account_credit_sum:
            debt_account_balance = debt_account_start_state - debt_account_credit_sum
            
        turnovers.append({"id": loan.id,
                          "local_code":loan.code,
                          "monitoring_case_id":loan.monitoring_case_id,
                          "main_responsible_id":loan.main_responsible_id,
                          "second_responsible_id":loan.second_responsible_id,
                          'state_chain_name':loan.state_chain_name,
                          "loan_client":loan_client,
                          "loan_id":loan.loan_id,
                          "client_name":loan.client_name,
                          "loan_id":loan.loan_id,
                          "client_name":loan.client_name,
                          "currency":loan.currency_code,
                          "debt_account_start_state":loan.debt_account_start_state,
                          "debt_account_credit_sum":loan.debt_account_credit_sum,
                          "debt_account_balance":debt_account_balance,
                          "account_16377_start_state":loan.account_16377_start_state,
                          "account_16377_debit_sum":loan.account_16377_debit_sum,
                          "account_16377_credit_sum":loan.account_16377_credit_sum,
                          "account_16377_balance":account_16377_start_state + account_16377_debit_sum - account_16377_credit_sum,
                          "account_163xx_start_state":loan.account_163xx_start_state,
                          "account_163xx_debit_sum":loan.account_163xx_debit_sum,
                          "account_163xx_credit_sum":loan.account_163xx_credit_sum,
                          "account_163xx_balance":account_163xx_start_state + account_163xx_debit_sum - account_163xx_credit_sum,
                          "lead_last_date":loan.lead_last_date,
                          "kad_letter_35":KGT.SEND_1_LETTER.value,
                          "kad_letter_45":KGT.SEND_2_LETTER.value,
                          })
        
    
    return {"items": turnovers,
            "total":count,
            "page":page,
            "size":size}
   