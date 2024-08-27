import datetime
from sqlalchemy import or_, and_
import sqlalchemy
from sqlalchemy.sql import text
from sqlalchemy.sql.expression import cast, extract
from ...models.business_case.business_case_model import BusinessCase
from ...models.brief_case.loan_portfolio import Loan_Portfolio
from ...models.monitoring_task_manager.task_manager_model import TaskManager
from ...models.users.users import Users as users_model
from ...models.brief_case.directories.loan_product import loan_product
from ...common.commit import flush_object
from ...models.brief_case.directories.bank_mfo import bank_mfo
from ...models.brief_case.directories.local_code import local_code
from ...models.brief_case.directories.currency import currency
from ...models.statuses.business_case_status_model import BusinessCaseStatus
from ...common.dictionaries.monitoring_case_dictionary import loan_case
from ...common.dictionaries.from_type import FromType
from sqlalchemy.orm import aliased
from sqlalchemy import case
from ...models.brief_case.loan_portfolio_schedule import LoanPortfolioSchedule
from calendar import monthrange


def create_business_case_with_append_task(task, data, from_type, db_session):#used
    new_loan_case = BusinessCase(loan_portfolio_id = data.loan_portfolio_id,
                                 main_responsible_id = data.main_responsible_id,
                                 deadline_extension_status_id = 1,
                                 second_responsible_id = data.second_responsible_id,
                                 business_case_status_id = loan_case['Новый'],
                                 from_type_id = from_type,
                                 task_manager_id = task.id,
                                 created_at = datetime.datetime.now(),
                                 updated_at = datetime.datetime.now()
                                 )
    db_session.add(new_loan_case)
    flush_object(db_session)
    return new_loan_case

from sqlalchemy.sql import func

def get_all_business_case(size, page, region_id, local_code_id, loan_id, client_name, is_target, product_type, client_type, \
    second_responsible, client_code,  user_id,  db_session):
    
    main_user = aliased(users_model)
    second_user = aliased(users_model)
    loan_portfolio2 = aliased(Loan_Portfolio)
   
            
    period = datetime.date.today()
    overdue_max_date_case = case(
                        [
                            (and_(Loan_Portfolio.overdue_start_date != None, Loan_Portfolio.date_overdue_percent != None,
                                  Loan_Portfolio.overdue_start_date <= Loan_Portfolio.date_overdue_percent), Loan_Portfolio.overdue_start_date),
                            (and_(Loan_Portfolio.overdue_start_date != None, Loan_Portfolio.date_overdue_percent != None,
                                  Loan_Portfolio.overdue_start_date > Loan_Portfolio.date_overdue_percent), Loan_Portfolio.overdue_start_date),
                           (and_(Loan_Portfolio.overdue_start_date != None, Loan_Portfolio.date_overdue_percent == None), Loan_Portfolio.overdue_start_date),
                           (and_(Loan_Portfolio.overdue_start_date == None, Loan_Portfolio.date_overdue_percent != None), Loan_Portfolio.date_overdue_percent)
                        ], else_=None).label("overdue_max_date")
    all_duty = case([
        (and_(Loan_Portfolio.overdue_balance != None, Loan_Portfolio.balance_16377 != None), 
         cast(Loan_Portfolio.overdue_balance, sqlalchemy.FLOAT) + cast(Loan_Portfolio.balance_16377, sqlalchemy.FLOAT)),
        (and_(Loan_Portfolio.overdue_balance != None, Loan_Portfolio.balance_16377 == None), 
         cast(Loan_Portfolio.overdue_balance, sqlalchemy.FLOAT)),
        (and_(Loan_Portfolio.overdue_balance == None, Loan_Portfolio.balance_16377 != None), 
         cast(Loan_Portfolio.balance_16377, sqlalchemy.FLOAT)),
        ], else_=None).label('all_duty')
    
    schedule_sum = case([(func.sum(cast(LoanPortfolioSchedule.summ_red, sqlalchemy.FLOAT)/100)==None, 0)], else_=func.sum(cast(LoanPortfolioSchedule.summ_red, sqlalchemy.FLOAT)/100)).label('schedule_sum')
    
    sub_query_schedule_sum = db_session.query(schedule_sum).join(loan_portfolio2, loan_portfolio2.loan_id==LoanPortfolioSchedule.loan_id, isouter=True)\
        .filter(loan_portfolio2.loan_id==Loan_Portfolio.loan_id)\
        .filter(loan_portfolio2.status==1)\
        .filter(LoanPortfolioSchedule.date_red>=datetime.datetime.now()).scalar_subquery()
        
    main_user_case = case([(BusinessCase.main_responsible_id == user_id, second_user.full_name)], else_=None).label("full_name")
    business_case = db_session.query(BusinessCase.id,
                                    BusinessCaseStatus.id.label('business_status_id'),
                                    BusinessCaseStatus.name.label('business_status_name'),
                                    main_user_case,
                                    overdue_max_date_case,
                                    Loan_Portfolio.id.label('loan_portfolio_id'),
                                    Loan_Portfolio.loan_id,
                                    Loan_Portfolio.client_name,
                                    Loan_Portfolio.total_overdue,
                                    all_duty,
                                    Loan_Portfolio.overdue_balance,
                                    Loan_Portfolio.overdue_start_date,
                                    Loan_Portfolio.balance_16377,
                                    Loan_Portfolio.date_overdue_percent,
                                    LoanPortfolioSchedule.id.label('loan_schedule_id'),
                                    LoanPortfolioSchedule.date_red.label('repayment_date'),
                                    LoanPortfolioSchedule.summ_red.label('recommended_amount'),
                                    # summ_red_case,
                                    sub_query_schedule_sum.label('total_overdue_by_graph'),
                                    local_code.code.label('local_code'),
                                    currency.code.label('currency_code'),
                                    TaskManager.general_task_id,
                                    BusinessCase.created_at
                            )\
                .join(Loan_Portfolio, BusinessCase.loan_portfolio_id == Loan_Portfolio.id, isouter=False)\
                .join(TaskManager, BusinessCase.task_manager_id == TaskManager.id, isouter=True)\
                .join(BusinessCaseStatus, BusinessCase.business_case_status_id == BusinessCaseStatus.id, isouter=True)\
                .join(main_user, BusinessCase.main_responsible_id == main_user.id, isouter=True)\
                .join(second_user, BusinessCase.second_responsible_id == second_user.id, isouter=True)\
                .join(local_code, Loan_Portfolio.local_code_id == local_code.id, isouter=True)\
                .join(currency, Loan_Portfolio.currency_id == currency.id, isouter=True)\
                .join(LoanPortfolioSchedule, LoanPortfolioSchedule.loan_id == Loan_Portfolio.loan_id, isouter=True)\
                .filter(or_(BusinessCase.main_responsible_id == user_id, BusinessCase.second_responsible_id == user_id))\
                .filter(Loan_Portfolio.status == 1)\
                .filter(Loan_Portfolio.is_taken_business == True)\
                .filter(all_duty!=None).filter(all_duty!=0)\
                .filter(extract('month', LoanPortfolioSchedule.date_red) == period.month)\
                .filter(extract('year', LoanPortfolioSchedule.date_red) == period.year)\
                    
                 
    if region_id is not None:
        business_case = business_case.filter(Loan_Portfolio.client_region == region_id)
    
    if local_code_id is not None:
        business_case = business_case.filter(Loan_Portfolio.local_code_id == local_code_id)
    
    if loan_id is not None or client_name is not None:
        business_case = business_case.filter(or_(cast(Loan_Portfolio.loan_id, sqlalchemy.Text).like(f'{loan_id}%'), Loan_Portfolio.client_name.ilike(f'%{client_name}%')))
    
    if second_responsible is not None:
        business_case = business_case.filter(BusinessCase.second_responsible_id == second_responsible)
    
    if is_target is not None:
        business_case = business_case.filter(loan_product.name == Loan_Portfolio.loan_product)\
        .filter(loan_product.is_target == is_target)
    
    if product_type is not None:
        business_case = business_case.filter(loan_product.name == Loan_Portfolio.loan_product)\
        .filter(loan_product.type == product_type) 
    
    if client_type is not None:    
        if client_type != '11' and client_type != '08':
            business_case = business_case.filter(Loan_Portfolio.borrower_type.regexp_match('^(?!08|11).*'))
        else:
            business_case = business_case.filter(Loan_Portfolio.borrower_type.regexp_match(f'^({client_type}).*'))
    
    if client_code is not None:
        business_case = business_case.filter(Loan_Portfolio.loan_account.regexp_match('\d{9}' + str(client_code) + '\d*' + '\d{3}'))
        
            
    business_case = business_case.order_by(Loan_Portfolio.overdue_balance.asc(),Loan_Portfolio.balance_16377.asc())
        
    count = business_case.count()
    business_case = business_case.limit(size).offset((page-1)*size).all()
    
    business_case_list = []
    
    for business in business_case:
        recommended_amount = business.recommended_amount and float(business.recommended_amount)/100 or None
        loan_client = business.loan_id
        if business.client_name is not None:
            loan_client = str(business.loan_id) +' : '+ business.client_name
        total_overdue = 0
        total_overdue_by_graph = 0
        if business.total_overdue is not None and  business.total_overdue !='0':
            total_overdue = business.total_overdue
        if business.total_overdue_by_graph is not None and business.total_overdue_by_graph!=0:
            total_overdue_by_graph = business.total_overdue_by_graph/100
        if float(total_overdue) < total_overdue_by_graph:
            recommended_amount = 0
        if (business.all_duty == 0 or business.all_duty is None) and recommended_amount == 0:
            continue
        
        business_case_list.append({"id":business.id,
                               "loan_portfolio": {"id":business.loan_portfolio_id,
                                                  "local_code": business.local_code,
                                                  "total_overdue": business.total_overdue,
                                                  "loan_client":loan_client,
                                                  "loan_id":business.loan_id,
                                                  "client_name":business.client_name,
                                                  "all_duty": business.all_duty,
                                                  "overdue_balance": business.overdue_balance,
                                                  "overdue_max_date": business.overdue_max_date,
                                                  "overdue_start_date": business.overdue_start_date,
                                                  "balance_16377": business.balance_16377,
                                                  "date_overdue_percent": business.date_overdue_percent,
                                                  "total_overdue_by_graph": business.total_overdue_by_graph
                                                  },
                               "loan_portfolio_schedule": {
                                   "id": business.loan_schedule_id,
                                   "repayment_date": business.repayment_date,
                                   "recommended_amount":recommended_amount,
                                   "currency_code":business.currency_code
                               },
                               "responsible": {"full_name":business.full_name},
                               "general_task":business.general_task_id,
                               "case_status": {"id": business.business_status_id,
                                               "name": business.business_status_name},
                               "created_at":business.created_at})
    
    return {"items": business_case_list,
            "total":count,
            "page":page,
            "size":size} 


def get_loan_portfolio_schedule(period, loan_id, db_session):
    return db_session.query(LoanPortfolioSchedule).filter(LoanPortfolioSchedule.loan_id == loan_id)\
        .filter(extract('month', LoanPortfolioSchedule.repayment_date) == period.month)\
            .filter(extract('year', LoanPortfolioSchedule.repayment_date) == period.year).first()


def get_business_data_for_main_page(db_session):
    
    data = db_session.query(func.count(Loan_Portfolio.id).label('loan_count'), \
                            func.sum(cast(Loan_Portfolio.total_overdue, sqlalchemy.FLOAT)).label('total_overdue'),\
                            func.sum(cast(Loan_Portfolio.overdue_balance, sqlalchemy.FLOAT)).label('overdue_balance'),\
                            func.sum(cast(Loan_Portfolio.balance_16377, sqlalchemy.FLOAT)).label('balance_16377'),\
                            (func.sum(cast(Loan_Portfolio.overdue_balance, sqlalchemy.FLOAT)) + func.sum(cast(Loan_Portfolio.balance_16377, sqlalchemy.FLOAT))).label('all_duty'))\
        .filter(Loan_Portfolio.status == 1).first()

    overdue_loan = db_session.query(func.count(Loan_Portfolio.id).label('overdue_loan_count'))\
        .filter(Loan_Portfolio.overdue_balance != None).filter(Loan_Portfolio.balance_16377 != None).filter(Loan_Portfolio.status == 1).first()

    return {"loan_count":data.loan_count,
            "total_overdue":data.total_overdue,
            "overdue_balance":data.overdue_balance,
            "balance_16377":data.balance_16377,
            "all_duty":data.all_duty,
            "overdue_loan_count":overdue_loan.overdue_loan_count}
    