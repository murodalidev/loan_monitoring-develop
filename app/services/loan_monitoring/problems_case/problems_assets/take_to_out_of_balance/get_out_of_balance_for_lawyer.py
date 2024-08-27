from datetime import datetime, timedelta

from app.models.problems_case.out_of_balance.out_of_balance_model import OutOfBalance
from ......models.brief_case.loan_portfolio import Loan_Portfolio
from ......models.problems_case.problems_case_model import ProblemsCase
from ......models.users.users import Users as users_model
from sqlalchemy.orm import aliased
from sqlalchemy import case, and_, or_
from sqlalchemy.sql.expression import cast, extract
from sqlalchemy.sql import func
import sqlalchemy
from ......models.statuses.problems_case_status_model import ProblemsCaseStatus
from ......models.brief_case.directories.bank_mfo import bank_mfo
from ......models.brief_case.directories.local_code import local_code
from ......models.brief_case.directories.client_region import client_region
from ......models.brief_case.directories.currency import currency
from ......models.brief_case.directories.loan_product import loan_product
from ......services.monitoring_files import files_crud


def get_all_out_of_balance_for_lawyer(size, page, region_id, local_code_id, loan_id, client_name, is_target, product_type, client_type, \
    client_code, total_overdue_asc_desc, user, second_responsible, department, db_session):
    user_roles = []
    for role in user.roles:
        user_roles.append(role.name)
    main_user = aliased(users_model)
    second_user = aliased(users_model)
   
            
    overdue_max_date_case = case(
                        [
                            (and_(Loan_Portfolio.overdue_start_date != None, Loan_Portfolio.date_overdue_percent != None,
                                  Loan_Portfolio.overdue_start_date <= Loan_Portfolio.date_overdue_percent), Loan_Portfolio.overdue_start_date),
                            (and_(Loan_Portfolio.overdue_start_date != None, Loan_Portfolio.date_overdue_percent != None,
                                  Loan_Portfolio.overdue_start_date > Loan_Portfolio.date_overdue_percent), Loan_Portfolio.overdue_start_date),
                           (and_(Loan_Portfolio.overdue_start_date != None, Loan_Portfolio.date_overdue_percent == None), Loan_Portfolio.overdue_start_date),
                           (and_(Loan_Portfolio.overdue_start_date == None, Loan_Portfolio.date_overdue_percent != None), Loan_Portfolio.date_overdue_percent)
                        ], else_=None).label("overdue_max_date")
   
    
    
  

    problems_case = db_session.query(ProblemsCase.id,
                                    ProblemsCaseStatus.id.label('problem_status_id'),
                                    ProblemsCaseStatus.name.label('problem_status_name'),
                                    ProblemsCase.main_responsible_id,
                                    ProblemsCase.second_responsible_id,
                                    overdue_max_date_case,
                                    Loan_Portfolio.id.label('loan_portfolio_id'),
                                    Loan_Portfolio.loan_id,
                                    Loan_Portfolio.client_name,
                                    Loan_Portfolio.total_overdue,
                                    Loan_Portfolio.overdue_balance,
                                    Loan_Portfolio.overdue_start_date,
                                    Loan_Portfolio.balance_16377,
                                    Loan_Portfolio.date_overdue_percent,
                                    client_region.name.label('region'),
                                    local_code.code.label('local_code'),
                                    currency.code.label('currency_code'),
                                    ProblemsCase.created_at
                            )\
                .join(Loan_Portfolio, ProblemsCase.loan_portfolio_id == Loan_Portfolio.id, isouter=False)\
                .join(ProblemsCaseStatus, ProblemsCase.problems_case_status_id == ProblemsCaseStatus.id, isouter=True)\
                .join(main_user, ProblemsCase.main_responsible_id == main_user.id, isouter=True)\
                .join(second_user, ProblemsCase.second_responsible_id == second_user.id, isouter=True)\
                .join(client_region, Loan_Portfolio.client_region == client_region.id, isouter=True)\
                .join(local_code, Loan_Portfolio.local_code_id == local_code.id, isouter=True)\
                .join(currency, Loan_Portfolio.currency_id == currency.id, isouter=True)\
                .join(OutOfBalance, OutOfBalance.problems_case_id == ProblemsCase.id)\
                .filter(Loan_Portfolio.status == 1)\
                            .order_by(ProblemsCase.updated_at.desc())
                        
                
                 
    # if region_id is not None:
    #     problems_case = problems_case.filter(Loan_Portfolio.client_region == region_id)
    
    # if local_code_id is not None:
    #     problems_case = problems_case.filter(Loan_Portfolio.local_code_id == local_code_id)
    
    if loan_id is not None or client_name is not None:
        problems_case = problems_case.filter(or_(cast(Loan_Portfolio.loan_id, sqlalchemy.Text).like(f'{loan_id}%'), Loan_Portfolio.client_name.ilike(f'%{client_name}%')))
    
    
    
    if 'problem_block_lawyer' in user_roles:
        problems_case = problems_case.filter(OutOfBalance.third_responsible_id != None)
    
    if product_type is not None:
        problems_case = problems_case.filter(loan_product.name == Loan_Portfolio.loan_product)\
        .filter(loan_product.type == product_type) 
    
    if client_type is not None:    
        if client_type != '11' and client_type != '08':
            problems_case = problems_case.filter(Loan_Portfolio.borrower_type.regexp_match('^(?!08|11).*'))
        else:
            problems_case = problems_case.filter(Loan_Portfolio.borrower_type.regexp_match(f'^({client_type}).*'))
    
    if client_code is not None:
        problems_case = problems_case.filter(Loan_Portfolio.loan_account.regexp_match('\d{9}' + str(client_code) + '\d*' + '\d{3}'))
        
            
    count = problems_case.count()
    problems_case = problems_case.limit(size).offset((page-1)*size).all()
    
    problems_case_list = []
    
    for problem in problems_case:
        if problem.client_name is not None:
            loan_client = str(problem.loan_id) +' : '+ problem.client_name
        
        problems_case_list.append({"id":problem.id,
                               "loan_portfolio": {"id":problem.loan_portfolio_id,
                                                  "region": problem.region,
                                                  "local_code": problem.local_code,
                                                  "total_overdue": problem.total_overdue,
                                                  "loan_client":loan_client,
                                                  "loan_id":problem.loan_id,
                                                  "client_name":problem.client_name,
                                                  "overdue_balance": problem.overdue_balance,
                                                  "overdue_start_date": problem.overdue_start_date,
                                                  "balance_16377": problem.balance_16377,
                                                  "date_overdue_percent": problem.date_overdue_percent
                                                  },
                               
                               "main_responsible": problem.main_responsible_id,
                               "second_responsible": problem.second_responsible_id,
                               "created_at":problem.created_at})
    
    return {"items": problems_case_list,
            "total":count,
            "page":page,
            "size":size} 






def get_out_of_balance_details(problem_case_id, db_session):
    out_of_balance_datas = {}
    out_of_balance = db_session.query(OutOfBalance).filter(OutOfBalance.problems_case_id == problem_case_id).first()
    
    if out_of_balance is not None:
        out_of_balance_datas ={"id":out_of_balance.id,
                            "main_responsible": out_of_balance.main_responsible_id and {"id":out_of_balance.main_responsible.id,
                                                                                         "full_name":out_of_balance.main_responsible.full_name} or None,
                            "second_responsible": out_of_balance.second_responsible_id and {"id":out_of_balance.second_responsible.id,
                                                                                         "full_name":out_of_balance.second_responsible.full_name} or None,
                            "third_responsible": out_of_balance.third_responsible_id and {"id":out_of_balance.third_responsible.id,
                                                                                         "full_name":out_of_balance.third_responsible.full_name} or None,
                            "turn": out_of_balance.turn and out_of_balance.turn or None,
                            "out_of_balance_status": out_of_balance.out_of_balance_status_id and out_of_balance.status or None,
                            "created_at":out_of_balance.created_at and out_of_balance.created_at or None,
                            "updated_at":out_of_balance.updated_at and out_of_balance.updated_at or None,
                            "files": out_of_balance.files and files_crud.get_case_files(out_of_balance) or None}
        
    return {"out_of_balance":out_of_balance_datas}