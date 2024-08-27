from datetime import datetime, timedelta

from app.models.problems_case.problems_assets.problems_assets_model import ProblemsAssets
from ......models.brief_case.loan_portfolio import Loan_Portfolio
from ......models.loan_case.loan_case_model import LoanCase
from ......models.loan_case.loan_case_history_model import LoanCaseHistory
from ......models.juridical_case.juridical_case_model import JuridicalCase
from ......models.problems_case.problems_case_model import ProblemsCase
from ......models.problems_case.problems_case_history import ProblemsCaseHistory
from ......models.problems_case.problems_monitoring_model import ProblemsMonitoring
from ....general_tasks import general_tasks_crud
from ....task_manager.task_manager_crud import TaskManager_class
from ......models.juridical_case.juridical_case_history_model import JuridicalCaseHistory
from  app.services.loan_monitoring.problems_case import letters_crud
from  app.services.users.users_crud import Users as users
from ......common.commit import commit_object, flush_object
from ......common.is_empty import is_empty, is_exists, is_empty_list
from ......schemas.task_manager_schemas import UpdateTaskManagerSetResponsible, UpdateTaskManagerClose,UpdateTaskManagerAccept
from ......schemas.notification_schemas import CreateNotification
from ......models.files.monitoring_files_model import MonitoringFiles
from ....notification.notification_crud import Notificaton_class
from ......common.dictionaries import notification_dictionary, task_status_dictionaries
from ......common.dictionaries.task_status_dictionaries import task_status
from ......common.dictionaries.monitoring_case_dictionary import problems_case, problems_monitoring, letter_status, juridic_case
from ......common.dictionaries.case_history_dictionaries import problem_case_history, loan_case_history, juridical_case_history
from ......common.dictionaries.departments_dictionary import DEP
from ......common.dictionaries.general_tasks_dictionary import JGT, MGT, PGT, GTCAT
from ......common.dictionaries.monitoring_case_dictionary import loan_case
from ......models.users.users import Users as users_model
from sqlalchemy.orm import aliased
from sqlalchemy import case, and_, or_
from sqlalchemy.sql.expression import cast, extract
from sqlalchemy.sql import func
import sqlalchemy
from ......models.brief_case.loan_portfolio_schedule import LoanPortfolioSchedule
from ......models.statuses.problems_case_status_model import ProblemsCaseStatus
from ......models.brief_case.directories.bank_mfo import bank_mfo
from ......models.brief_case.directories.local_code import local_code
from ......models.brief_case.directories.client_region import client_region
from ......models.brief_case.directories.currency import currency
from ......models.monitoring_task_manager.task_manager_model import TaskManager
from ......models.brief_case.directories.loan_product import loan_product



def get_all_problems_assets_for_lawyer(size, page, region_id, local_code_id, loan_id, client_name, is_target, product_type, client_type, \
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
   
    subquery_problems_assets = db_session.query(ProblemsAssets.problems_case_id).distinct(ProblemsAssets.problems_case_id)
    
    
    if 'problem_block_lawyer' in user_roles:
        subquery_problems_assets = subquery_problems_assets.filter(ProblemsAssets.third_responsible_id != None)
    
    
    subquery_problems_assets.subquery()

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
                    .filter(ProblemsCase.id.in_(subquery_problems_assets))\
                .filter(Loan_Portfolio.status == 1)\
                            .order_by(ProblemsCase.updated_at.desc())
                        
                
                 
    # if region_id is not None:
    #     problems_case = problems_case.filter(Loan_Portfolio.client_region == region_id)
    
    # if local_code_id is not None:
    #     problems_case = problems_case.filter(Loan_Portfolio.local_code_id == local_code_id)
    
    if loan_id is not None or client_name is not None:
        problems_case = problems_case.filter(or_(cast(Loan_Portfolio.loan_id, sqlalchemy.Text).like(f'{loan_id}%'), Loan_Portfolio.client_name.ilike(f'%{client_name}%')))
    
    
    
    
    
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

