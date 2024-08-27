import datetime
from sqlalchemy import or_, and_
import sqlalchemy
from sqlalchemy.sql.expression import cast

from app.services.loan_monitoring.problems_case.problems_case_crud import get_state_chain_status
from ....models.problems_case.problems_case_model import ProblemsCase
from app.models.brief_case.directories.currency import currency
from ....models.brief_case.loan_portfolio import Loan_Portfolio
from ....models.balance_turnover.balance_turnover_model import BalanceTurnover
from ....models.problems_case.problems_case_history import ProblemsCaseHistory
from ....models.problems_case.problems_monitoring_model import ProblemsMonitoring
from app.models.problems_case.problem_state_chain_model import ProblemStateChain
from app.models.problems_case.auction.auction_model import ProblemsAuction
from app.models.problems_case.judicial_process.judicial_process_data_model import JudicialData
from app.models.problems_case.mib_ended.mib_model import ProblemsMib
from app.models.problems_case.out_of_balance.out_of_balance_model import OutOfBalance
from app.models.problems_case.problems_assets.problems_assets_model import ProblemsAssets
from app.models.problems_case.problem_states_model import ProblemStates
from ....models.brief_case.directories.loan_product import loan_product
from ....models.loan_case.loan_case_model import LoanCase
from ....models.brief_case.directories.local_code import local_code
from sqlalchemy import case



def get_out_of_balance_all_turnover(size, page, user, region_id,local_code_id,client_name, loan_id, task_status, state_chain,  product_type, 
                                    main_responsible, second_responsible, client_type, db_session):
    user_roles = []
    for role in user.roles:
        user_roles.append(role.name)
    account_95413_start_state = case(
                        [
                            (BalanceTurnover.account_95413_start_state != None, cast(BalanceTurnover.account_95413_start_state, sqlalchemy.FLOAT))
                        ], else_=0).label("account_95413_start_state")
    account_9150x_start_state = case(
                        [
                            (BalanceTurnover.account_9150x_start_state != None, cast(BalanceTurnover.account_9150x_start_state, sqlalchemy.FLOAT))
                        ], else_=0).label("account_9150x_start_state")
    
    account_95413_credit_sum = case(
                        [
                            (BalanceTurnover.account_95413_credit_sum != None, cast(BalanceTurnover.account_95413_credit_sum, sqlalchemy.FLOAT)/100)
                        ], else_=0).label("account_95413_credit_sum")
    
    account_95413_debit_sum = case(
                        [
                            (BalanceTurnover.account_95413_debit_sum != None, cast(BalanceTurnover.account_95413_debit_sum, sqlalchemy.FLOAT)/100)
                        ], else_=0).label("account_95413_debit_sum")
    
    account_9150x_credit_sum = case(
                        [
                            (BalanceTurnover.account_9150x_credit_sum != None, cast(BalanceTurnover.account_9150x_credit_sum, sqlalchemy.FLOAT)/100)
                        ], else_=0).label("account_9150x_credit_sum")
    
    account_9150x_debit_sum = case(
                        [
                            (BalanceTurnover.account_9150x_debit_sum != None, cast(BalanceTurnover.account_9150x_debit_sum, sqlalchemy.FLOAT)/100)
                        ], else_=0).label("account_9150x_debit_sum")
        
    get_turnover = db_session.query(Loan_Portfolio.id,
                                    local_code.code, 
                                    LoanCase.monitoring_case_id.label("monitoring_case_id"),
                                    ProblemsCase.id.label('problems_id'),
                                    currency.code.label('currency_code'), 
                                    ProblemStates.name.label('state_chain_name'),
                                    ProblemStates.id.label('state_chain_id'),
                                    Loan_Portfolio.loan_id, 
                                    Loan_Portfolio.client_name,
                                    account_95413_start_state,
                                    account_9150x_start_state,
                                    account_95413_credit_sum,
                                    account_95413_debit_sum,
                                    account_9150x_credit_sum,
                                    account_9150x_debit_sum, 
                                    BalanceTurnover.lead_last_date)\
                            .join(Loan_Portfolio, ProblemsCase.loan_portfolio_id == Loan_Portfolio.id)\
                                .join(LoanCase, LoanCase.loan_portfolio_id == ProblemsCase.loan_portfolio_id, isouter=True)\
                        .join(BalanceTurnover, Loan_Portfolio.loan_id == BalanceTurnover.loan_id, isouter=True)\
                            .join(ProblemStateChain, ProblemStateChain.loan_id == Loan_Portfolio.loan_id, isouter = True)\
                            .join(ProblemStates, ProblemStates.id == ProblemStateChain.last_state_id, isouter = True)\
                            .join(local_code, local_code.id == Loan_Portfolio.local_code_id)\
                                .join(currency, Loan_Portfolio.currency_id==currency.id)\
                                .where(or_(and_(BalanceTurnover.account_95413_start_state!=None, BalanceTurnover.account_95413_start_state!=0),
                                            and_(BalanceTurnover.account_9150x_start_state!=None, BalanceTurnover.account_9150x_start_state!=0),
                                            and_(BalanceTurnover.account_95413_credit_sum!=None, BalanceTurnover.account_95413_credit_sum!=0),
                                            and_(BalanceTurnover.account_95413_debit_sum!=None, BalanceTurnover.account_95413_debit_sum!=0),
                                            and_(BalanceTurnover.account_9150x_credit_sum!=None, BalanceTurnover.account_9150x_credit_sum!=0),
                                            and_(BalanceTurnover.account_9150x_debit_sum!=None, BalanceTurnover.account_9150x_debit_sum!=0)))\
                                .where(Loan_Portfolio.status == 1).where(Loan_Portfolio.is_taken_out_of_balance == True)
    if region_id is not None:
        get_turnover = get_turnover.filter(Loan_Portfolio.client_region == region_id)
    
    
        
    if product_type is not None:
        get_turnover = get_turnover.join(loan_product, loan_product.name == Loan_Portfolio.loan_product)\
        .filter(loan_product.type == product_type) 
    
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
    
    
    if state_chain is not None:
        
        get_turnover = get_turnover.filter(ProblemStates.id == state_chain)
        
        if state_chain == 4:
            get_turnover = get_turnover.join(JudicialData, ProblemsCase.id == JudicialData.problems_case_id)
            if task_status is not None:
                get_turnover = get_turnover.filter(JudicialData.judicial_status_id == task_status)
                
        if state_chain == 6:
            get_turnover = get_turnover.join(ProblemsAssets, ProblemsCase.id == ProblemsAssets.problems_case_id)
            if task_status is not None:
                get_turnover = get_turnover.filter(ProblemsAssets.assets_status_id == task_status)
                
        if state_chain == 7:
            get_turnover = get_turnover.join(OutOfBalance, ProblemsCase.id == OutOfBalance.problems_case_id)
            if task_status is not None:
                get_turnover = get_turnover.filter(OutOfBalance.out_of_balance_status_id == task_status)
                
                
        if state_chain == 8:
            get_turnover = get_turnover.join(ProblemsAuction, ProblemsCase.id == ProblemsAuction.problems_case_id)
            if task_status is not None:
                get_turnover = get_turnover.filter(ProblemsAuction.auction_status_id == task_status)
                
                
        if state_chain == 9:
            get_turnover = get_turnover.join(ProblemsMib, ProblemsCase.id == ProblemsMib.problems_case_id)
            if task_status is not None:
                get_turnover = get_turnover.filter(ProblemsMib.mib_ended_status_id == task_status)
    
    
    if local_code_id is not None:
        get_turnover = get_turnover.filter(Loan_Portfolio.local_code_id == local_code_id)
    
    if second_responsible is not None:
        get_turnover = get_turnover.filter(ProblemsCase.second_responsible_id == second_responsible)
    
    
    if client_type is not None:    
        if client_type != '11' and client_type != '08':
            get_turnover = get_turnover.filter(Loan_Portfolio.borrower_type.regexp_match('^(?!08|11).*'))
        else:
            get_turnover = get_turnover.filter(Loan_Portfolio.borrower_type.regexp_match(f'^({client_type}).*'))
    
    if loan_id is not None or client_name is not None:
        get_turnover = get_turnover.filter(or_(cast(Loan_Portfolio.loan_id, sqlalchemy.Text).like(f'{loan_id}%'), Loan_Portfolio.client_name.ilike(f'%{client_name}%')))
    count = get_turnover.count()
    
    get_turnover = get_turnover.limit(size).offset((page-1)*size).all()
    turnovers = []
    for loan in get_turnover:
        
        state_chain_status = get_state_chain_status(loan.state_chain_id, loan.id, db_session)
        
        
        loan_client = loan.loan_id
        if loan.client_name is not None:
            loan_client = str(loan.loan_id) +' : '+ loan.client_name
        account_95413_start_state =0
        if loan.account_95413_start_state is not None:
            account_95413_start_state = loan.account_95413_start_state
        account_9150x_start_state = 0
        if loan.account_9150x_start_state is not None:
            account_9150x_start_state = loan.account_9150x_start_state
        account_95413_credit_sum = 0
        if loan.account_95413_credit_sum is not None:
            account_95413_credit_sum = loan.account_95413_credit_sum
        account_95413_debit_sum = 0
        if loan.account_95413_debit_sum is not None:
            account_95413_debit_sum = loan.account_95413_debit_sum
        account_9150x_credit_sum = 0
        if loan.account_9150x_credit_sum is not None:
            account_9150x_credit_sum = loan.account_9150x_credit_sum
        account_9150x_debit_sum = 0
        if loan.account_9150x_debit_sum is not None:
            account_9150x_debit_sum = loan.account_9150x_debit_sum
        account_95413_balance = 0
        if account_95413_start_state > (account_95413_credit_sum - account_95413_debit_sum):
            account_95413_balance = account_95413_start_state - (account_95413_credit_sum - account_95413_debit_sum)
        turnovers.append({"id": loan.id,
                          'state_chain_name':loan.state_chain_name,
                          'state_chain_status':state_chain_status,
                          "local_code":loan.code,
                          "loan_client":loan_client,
                          "loan_id":loan.loan_id,
                          "monitoring_case_id":loan.monitoring_case_id,
                          "client_name":loan.client_name,
                          "currency":loan.currency_code,
                          "account_95413_start_state":account_95413_start_state,
                          "account_95413_credit_sum":account_95413_credit_sum,
                          "account_95413_debit_sum":account_95413_debit_sum,
                          "account_95413_balance":account_95413_balance,
                          "account_9150x_start_state":account_9150x_start_state,
                          "account_9150x_debit_sum":account_9150x_debit_sum,
                          "account_9150x_credit_sum":account_9150x_credit_sum,
                          "account_9150x_balance":account_9150x_start_state + account_9150x_debit_sum - account_9150x_credit_sum,
                          "lead_last_date":loan.lead_last_date
                          })
        
    
    return {"items": turnovers,
            "total":count,
            "page":page,
            "size":size}