import datetime
from sqlalchemy import or_, and_
import sqlalchemy
from sqlalchemy.sql.expression import cast
from ...models.business_case.business_case_model import BusinessCase
from app.models.brief_case.directories.currency import currency
from ...models.brief_case.loan_portfolio import Loan_Portfolio
from ...models.balance_turnover.balance_turnover_model import BalanceTurnover
from ...models.brief_case.directories.loan_product import loan_product
from ...models.brief_case.directories.local_code import local_code
from sqlalchemy import case



def get_business_all_turnover(size, page, user, region_id,local_code_id,client_name, loan_id,  product_type, client_type, main_responsible, second_responsible, db_session):
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
                                    BusinessCase.id.label('business_id'),
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
                            .join(Loan_Portfolio, BusinessCase.loan_portfolio_id == Loan_Portfolio.id)\
                        .join(BalanceTurnover, Loan_Portfolio.loan_id == BalanceTurnover.loan_id, isouter=True)\
                            .join(local_code, local_code.id == Loan_Portfolio.local_code_id)\
                                .join(currency, Loan_Portfolio.currency_id==currency.id)\
                                .where(or_(and_(Loan_Portfolio.date_overdue_percent== None, Loan_Portfolio.overdue_start_date != None, (current_date-Loan_Portfolio.overdue_start_date)<31), 
and_(Loan_Portfolio.overdue_start_date == None, Loan_Portfolio.date_overdue_percent != None, (current_date-Loan_Portfolio.date_overdue_percent)<31),
and_(Loan_Portfolio.date_overdue_percent != None, Loan_Portfolio.overdue_start_date != None, Loan_Portfolio.overdue_start_date < Loan_Portfolio.date_overdue_percent, (current_date-Loan_Portfolio.overdue_start_date)<31),
and_(Loan_Portfolio.date_overdue_percent != None, Loan_Portfolio.overdue_start_date != None, Loan_Portfolio.overdue_start_date >= Loan_Portfolio.date_overdue_percent, (current_date-Loan_Portfolio.date_overdue_percent)<31)))\
                                .where(or_(and_(BalanceTurnover.debt_account_start_state!=None, BalanceTurnover.debt_account_start_state!=0),
                                            and_(BalanceTurnover.debt_account_credit_sum!=None, BalanceTurnover.debt_account_credit_sum!=0),
                                            and_(BalanceTurnover.account_16377_start_state!=None, BalanceTurnover.account_16377_start_state!=0),
                                            and_(BalanceTurnover.account_16377_debit_sum!=None, BalanceTurnover.account_16377_debit_sum!=0),
                                            and_(BalanceTurnover.account_16377_credit_sum!=None, BalanceTurnover.account_16377_credit_sum!=0),
                                            and_(BalanceTurnover.account_163xx_start_state!=None, BalanceTurnover.account_163xx_start_state!=0),
                                            and_(BalanceTurnover.account_163xx_debit_sum!=None, BalanceTurnover.account_163xx_debit_sum!=0),
                                            and_(BalanceTurnover.account_163xx_credit_sum!=None, BalanceTurnover.account_163xx_credit_sum!=0)))\
                                .where(Loan_Portfolio.status == 1)
    if region_id is not None:
        get_turnover = get_turnover.filter(Loan_Portfolio.client_region == region_id)
    
    if local_code_id is not None:
        get_turnover = get_turnover.filter(Loan_Portfolio.local_code_id == local_code_id)
    
    
    if 'superviser' in user_roles:
        local_code_id = user.local_code
            
    if  'business_block_filial_user' in user_roles:
            get_turnover = get_turnover.filter(BusinessCase.second_responsible_id == user.id)
    
    if 'business_block_filial_admin' in user_roles:
        get_turnover = get_turnover.filter(BusinessCase.second_responsible_id == user.id)
        
    if 'business_block_main_admin' in user_roles:
            get_turnover = get_turnover.filter(BusinessCase.main_responsible_id == user.id)
            
    if main_responsible is not None:
        if 'main_superviser' in user_roles or 'main_superviser_business' in user_roles:
            get_turnover = get_turnover.filter(BusinessCase.main_responsible_id == main_responsible)
    
    if second_responsible is not None:
        get_turnover = get_turnover.filter(BusinessCase.second_responsible_id == second_responsible)
    
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
                          "loan_client":loan_client,
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
                          "lead_last_date":loan.lead_last_date
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