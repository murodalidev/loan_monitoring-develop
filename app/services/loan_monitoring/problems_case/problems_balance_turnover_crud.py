import datetime
from sqlalchemy import or_, and_
import sqlalchemy
from sqlalchemy.sql.expression import cast

from app.models.problems_case.problems_monitoring_model import ProblemsMonitoring
from app.models.statuses.montoring_status_model import MonitoringStatus
from app.services.loan_monitoring.problems_case.problems_case_crud import get_problems_monitoring
from ....models.problems_case.problems_case_model import ProblemsCase
from app.models.brief_case.directories.currency import currency
from ....models.brief_case.loan_portfolio import Loan_Portfolio
from ....models.balance_turnover.balance_turnover_model import BalanceTurnover
from app.models.problems_case.problem_state_chain_model import ProblemStateChain
from app.models.problems_case.problem_states_model import ProblemStates
from ....models.loan_case.loan_case_model import LoanCase
from ....models.brief_case.directories.loan_product import loan_product
from ....models.brief_case.directories.local_code import local_code
from sqlalchemy import case



def get_problems_all_turnover(size, page, user, region_id,local_code_id,client_name, currency_id, loan_id, task_status, state_chain,  product_type, client_type,
                              main_responsible, second_responsible, db_session):
    print(region_id)
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
                                    local_code.code, 
                                    ProblemsCase.id.label('problems_id'),
                                    currency.code.label('currency_code'), 
                                    Loan_Portfolio.loan_id, 
                                    Loan_Portfolio.client_name,
                                    ProblemStates.name.label('state_chain_name'),
                                    debt_account_start_state,
                                    debt_account_credit_sum, 
                                    account_16377_start_state, 
                                    account_16377_debit_sum,
                                    account_16377_credit_sum,
                                    account_163xx_start_state,
                                    account_163xx_debit_sum,
                                    account_163xx_credit_sum, 
                                    BalanceTurnover.lead_last_date,
                                    LoanCase.id.label("loan_case_id"),
                                    LoanCase.monitoring_case_id.label("monitoring_case_id"),
                                    MonitoringStatus.name.label('monitoring_status_name'),
                                    )\
                            .join(Loan_Portfolio, ProblemsCase.loan_portfolio_id == Loan_Portfolio.id)\
                            .join(LoanCase, LoanCase.loan_portfolio_id == Loan_Portfolio.id, isouter=True)\
                        .join(BalanceTurnover, Loan_Portfolio.loan_id == BalanceTurnover.loan_id, isouter=True)\
                            .join(ProblemStateChain, ProblemStateChain.loan_id == Loan_Portfolio.loan_id, isouter = True)\
                            .join(ProblemStates, ProblemStates.id == ProblemStateChain.last_state_id, isouter = True)\
                                .join(ProblemsMonitoring, ProblemsMonitoring.problems_case_id == ProblemsCase.id, isouter=True)\
                                    .join(MonitoringStatus, MonitoringStatus.id == ProblemsMonitoring.problems_monitoring_status_id, isouter=True)\
                            .join(local_code, local_code.id == Loan_Portfolio.local_code_id)\
                                .join(currency, Loan_Portfolio.currency_id==currency.id)\
                                .where(or_(and_(Loan_Portfolio.date_overdue_percent== None, Loan_Portfolio.overdue_start_date != None, (current_date-Loan_Portfolio.overdue_start_date)>60), 
and_(Loan_Portfolio.overdue_start_date == None, Loan_Portfolio.date_overdue_percent != None, (current_date-Loan_Portfolio.date_overdue_percent)>60),
and_(Loan_Portfolio.date_overdue_percent != None, Loan_Portfolio.overdue_start_date != None, Loan_Portfolio.overdue_start_date < Loan_Portfolio.date_overdue_percent, (current_date-Loan_Portfolio.overdue_start_date)>60),
and_(Loan_Portfolio.date_overdue_percent != None, Loan_Portfolio.overdue_start_date != None, Loan_Portfolio.overdue_start_date >= Loan_Portfolio.date_overdue_percent, (current_date-Loan_Portfolio.date_overdue_percent)>60)))\
                                .where(or_(and_(BalanceTurnover.debt_account_start_state!=None, BalanceTurnover.debt_account_start_state!=0),
                                            and_(BalanceTurnover.debt_account_credit_sum!=None, BalanceTurnover.debt_account_credit_sum!=0),
                                            and_(BalanceTurnover.account_16377_start_state!=None, BalanceTurnover.account_16377_start_state!=0),
                                            and_(BalanceTurnover.account_16377_debit_sum!=None, BalanceTurnover.account_16377_debit_sum!=0),
                                            and_(BalanceTurnover.account_16377_credit_sum!=None, BalanceTurnover.account_16377_credit_sum!=0),
                                            and_(BalanceTurnover.account_163xx_start_state!=None, BalanceTurnover.account_163xx_start_state!=0),
                                            and_(BalanceTurnover.account_163xx_debit_sum!=None, BalanceTurnover.account_163xx_debit_sum!=0),
                                            and_(BalanceTurnover.account_163xx_credit_sum!=None, BalanceTurnover.account_163xx_credit_sum!=0)))\
                                            .filter(Loan_Portfolio.is_taken_problem == True)\
                                            .filter(Loan_Portfolio.is_taken_non_target == False)\
                                            .filter(Loan_Portfolio.is_taken_out_of_balance == False)\
                                .where(Loan_Portfolio.status == 1)
    
    if 'superviser' in user_roles:
        local_code_id = user.local_code
        
    if 'problem_block_filial_user' in user_roles:
        get_turnover = get_turnover.filter(ProblemsCase.second_responsible_id == user.id)
    
    if 'problem_block_filial_admin' in user_roles:
        get_turnover = get_turnover.filter(ProblemsCase.second_responsible_id == user.id)
        
    if 'problem_block_main_admin' in user_roles:
        get_turnover = get_turnover.filter(ProblemsCase.main_responsible_id == user.id)
            
            
    if main_responsible is not None:
        if 'main_superviser' in user_roles or 'main_superviser_problem' in user_roles:
            get_turnover = get_turnover.filter(ProblemsCase.main_responsible_id == main_responsible)
    
    
    
    
    if region_id is not None:
        get_turnover = get_turnover.filter(Loan_Portfolio.client_region == region_id)
    
    if local_code_id is not None:
        print(local_code_id)
        get_turnover = get_turnover.filter(Loan_Portfolio.local_code_id == local_code_id)
        
    
    if currency_id is not None:
        get_turnover = get_turnover.filter(Loan_Portfolio.currency_id == currency_id)
    
    if second_responsible is not None:
        get_turnover = get_turnover.filter(ProblemsCase.second_responsible_id == second_responsible)
    
    if task_status is not None:
        get_turnover = get_turnover.filter(ProblemsMonitoring.problems_monitoring_status_id == task_status)
    
    if state_chain is not None:
        get_turnover = get_turnover.filter(ProblemStates.id == state_chain)
    
    if product_type is not None:
        get_turnover = get_turnover.join(loan_product, loan_product.name == Loan_Portfolio.loan_product)\
        .filter(loan_product.type == product_type) 
    
    if client_type is not None:    
        if client_type != '11' and client_type != '08':
            get_turnover = get_turnover.filter(Loan_Portfolio.borrower_type.regexp_match('^(?!08|11).*'))
        else:
            get_turnover = get_turnover.filter(Loan_Portfolio.borrower_type.regexp_match(f'^({client_type}).*'))
    
    if loan_id is not None or client_name is not None:
        get_turnover = get_turnover.filter(or_(cast(Loan_Portfolio.loan_id, sqlalchemy.Text).like(f'{loan_id}%'), Loan_Portfolio.client_name.ilike(f'%{client_name}%')))
    
    get_turnover = get_turnover.order_by(ProblemsCase.updated_at.desc())
    
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
        turnovers.append({"id":loan.problems_id,
                          "loan_portfolio_id": loan.id,
                          "local_code":loan.code,
                          "loan_client":loan_client,
                          "loan_id":loan.loan_id,
                          "client_name":loan.client_name,
                          'state_chain_name':loan.state_chain_name,
                          "problem_monitoring":loan.monitoring_status_name,
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
                          "loan_case_id":loan.loan_case_id,
                          "monitoring_case_id":loan.monitoring_case_id
                          })
        
    
    return {"items": turnovers,
            "total":count,
            "page":page,
            "size":size}
    
    
    # debt_account_start_state = 
    # debt_account_credit_sum = 
    
    # account_16377_start_state = 
    # account_16377_debit_sum = 
    # account_16377_credit_sum = 
    
    # account_163xx_start_state = 
    # account_163xx_debit_sum = 
    # account_163xx_credit_sum = 
    # lead_last_date = 