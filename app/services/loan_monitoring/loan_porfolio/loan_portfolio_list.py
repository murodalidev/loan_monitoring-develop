import datetime

from app.models.problems_case.problem_state_chain_model import ProblemStateChain
from app.models.problems_case.problem_states_model import ProblemStates
from ....models.brief_case.directories.loan_product import loan_product
from ....models.brief_case.loan_portfolio import Loan_Portfolio
from ....models.loan_case.loan_case_history_model import LoanCaseHistory
from ....models.problems_case.problems_case_history import ProblemsCaseHistory
from ....models.juridical_case.juridical_case_history_model import JuridicalCaseHistory
from ....models.problems_case.problems_case_model import ProblemsCase
from ....models.juridical_case.juridical_case_model import JuridicalCase
from ..task_manager.task_manager_crud import TaskManager_class
from ....schemas.loan_portfolio_schemas import UserAcceptedLoanData, CreateLoanCase
from ..loan_case import loan_case_crud
from ..monitoring_case import target_monitoring_crud
from ....schemas.notification_schemas import CreateNotification
from ..notification.notification_crud import Notificaton_class
from ....common.dictionaries import notification_dictionary
from app.services.loan_monitoring.problems_case import problems_case_crud
from ....models.brief_case.directories.loan_product import loan_product
from ..juridical_case import juridical_case_crud
from sqlalchemy import or_
import sqlalchemy
from sqlalchemy.sql.expression import cast
from  app.services.users.users_crud import Users as users
from ....schemas.task_manager_schemas import UpdateTaskManagerAccept
from ....common.commit import commit_object, flush_object
from ....common.dictionaries.case_history_dictionaries import loan_case_history, problem_case_history, juridical_case_history
from ....common.dictionaries.monitoring_case_dictionary import juridic_case, problems_case
from ....common.dictionaries.departments_dictionary import DEP
from ....common.dictionaries.general_tasks_dictionary import JGT, MGT, PGT, GTCAT

def get_loan_porfolio(page,size, region_id, local_code, loan_id, client_name, client_code, is_target, client_type, department, db_session):
    get_portfolio = db_session.query(Loan_Portfolio)
    
    if region_id is not None:
        get_portfolio = get_portfolio.filter(Loan_Portfolio.client_region == region_id) 
    
    if local_code != 48:
        get_portfolio = get_portfolio.filter(Loan_Portfolio.local_code_id == local_code)
    
        
    if department == DEP.PROBLEM.value:
        get_portfolio = get_portfolio.filter(ProblemsCase.loan_portfolio_id == Loan_Portfolio.id)\
            .filter(ProblemsCase.problems_case_status_id != problems_case['закрыт'])\
                .filter(Loan_Portfolio.is_taken_problem == False)
                
    elif department == DEP.JURIDIC.value:
        get_portfolio = get_portfolio.filter(JuridicalCase.loan_portfolio_id == Loan_Portfolio.id)\
            .filter(JuridicalCase.juridical_case_status_id != juridic_case['закрыт'])\
                .filter(Loan_Portfolio.is_taken_juridic == False)
            
    if loan_id is not None or client_name is not None:
        get_portfolio = get_portfolio.filter(or_(cast(Loan_Portfolio.loan_id, sqlalchemy.Text).like(f'{loan_id}%'), Loan_Portfolio.client_name.like(f'%{client_name}%')))
    
    if client_code is not None:
        get_portfolio = get_portfolio.filter(Loan_Portfolio.loan_account.regexp_match('\d{9}' + str(client_code) + '\d*' + '\d{3}'))
      

    if is_target is not None:
        get_portfolio = get_portfolio.filter(loan_product.name == Loan_Portfolio.loan_product)\
            .filter(loan_product.is_target == is_target)
            
    if client_type != '11' and client_type != '08':
        get_portfolio = get_portfolio.filter(Loan_Portfolio.borrower_type.regexp_match('^(?!08|11).*'))
    else:
        get_portfolio = get_portfolio.filter(Loan_Portfolio.borrower_type.regexp_match(f'^({client_type}).*'))
        
    
    get_portfolio = get_portfolio.filter(Loan_Portfolio.status == 1)
    count = get_portfolio.count()
    get_portfolio = get_portfolio.order_by(Loan_Portfolio.id.asc()).limit(size).offset((page-1)*size).all()
    
    portfolios = []
    if get_portfolio is not None:
        for portfolio in get_portfolio:
            if portfolio.loan_id is not None:
                loan_client = portfolio.loan_id
            if portfolio.client_name is not None:
                loan_client = str(loan_client) +' : '+ portfolio.client_name
                if department == DEP.PROBLEM.value:
                    is_taken = portfolio.is_taken_problem and  portfolio.is_taken_problem or None
                elif department == DEP.JURIDIC.value:
                    is_taken = portfolio.is_taken_juridic and  portfolio.is_taken_juridic or None
                else:
                    is_taken = portfolio.is_taken_loan and  portfolio.is_taken_loan or None
                                
            portfolios.append({"id":portfolio.id, 
                            "region": portfolio.region_id and portfolio.region or None,
                            "local_code": portfolio.local_code_id and portfolio.local_code or None,
                            "loan_client": loan_client,
                            "status": portfolio.status and portfolio.loan_status or None,
                            "borrower_type": portfolio.borrower_type and portfolio.borrower_type or None,
                            "responsible": portfolio.loan_case and portfolio.loan_case[0].main_responsible.full_name or None,
                            "loan_product": portfolio.loan_product and portfolio.loan_product or None,
                            'is_taken':is_taken})

    return {"items": portfolios,
            "total":count,
            "page":page,
            "size":size}     
    
    
def get_loan_portfolio_details(portfolio_id, db_session):
    get_loan_portfolio = db_session.query(Loan_Portfolio).filter(Loan_Portfolio.id == portfolio_id).first()
    
    get_state_chain = db_session.query(ProblemStateChain.id, ProblemStates.name).join(ProblemStates, ProblemStates.id == ProblemStateChain.last_state_id)\
                .filter(ProblemStateChain.loan_id == get_loan_portfolio.loan_id).first()
    loan_portfolio = {}
    get_loan_product = db_session.query(loan_product).filter(loan_product.name == get_loan_portfolio.loan_product).first()
    
    loan_prod = None
    if get_loan_product is not None:
        loan_prod = get_loan_product.is_target
    if get_loan_portfolio.loan_id is not None:
        loan_client = get_loan_portfolio.loan_id
    if get_loan_portfolio.client_name is not None:
        loan_client = str(loan_client) +' : '+ get_loan_portfolio.client_name
    loan_portfolio ={"id":get_loan_portfolio.id,
                     "client_uid": get_loan_portfolio.client_uid and get_loan_portfolio.client_uid or None,
                    "region":{ "id":get_loan_portfolio.region.id,
                                    "name":get_loan_portfolio.region.name},
                    "local_code":{"id":get_loan_portfolio.local_code.id,
                                  "code":get_loan_portfolio.local_code.code,
                                  "name":get_loan_portfolio.local_code.name,
                                  "address":get_loan_portfolio.local_code.address,
                                  "phone_number":get_loan_portfolio.local_code.phone_number,
                                  "manager":get_loan_portfolio.local_code.manager},
                    "state_chain_name":get_state_chain and get_state_chain.name or None,
                    "client_region":get_loan_portfolio.client_region and get_loan_portfolio.region.name or None,
                    "client_district": get_loan_portfolio.client_district and get_loan_portfolio.client_district or None,
                    "loan_id":get_loan_portfolio.loan_id,
                    "client_name":get_loan_portfolio.client_name,
                    "loan_client": loan_client,
                    "balance_account": get_loan_portfolio.balance_account and get_loan_portfolio.balance_account or None,
                    "loan_account": get_loan_portfolio.loan_account and get_loan_portfolio.loan_account or None,
                    "currency": { "id":get_loan_portfolio.currency.id,
                                    "code":get_loan_portfolio.currency.code,
                                    "name":get_loan_portfolio.currency.name},
                    "contract_amount": get_loan_portfolio.contract_amount and get_loan_portfolio.contract_amount or None,
                    "contract_amount_uz_currency": get_loan_portfolio.contract_amount_uz_currency and get_loan_portfolio.contract_amount_uz_currency or None,
                    "issue_date": get_loan_portfolio.issue_date and get_loan_portfolio.issue_date or None,
                    "maturity_date": get_loan_portfolio.maturity_date and get_loan_portfolio.maturity_date or None,
                    "term_type": get_loan_portfolio.term_type and get_loan_portfolio.term_type or None,
                    "num_and_date_contract":get_loan_portfolio.num_and_date_contract and get_loan_portfolio.num_and_date_contract or None,
                    "osn_cmp_percent": get_loan_portfolio.osn_cmp_percent and get_loan_portfolio.osn_cmp_percent or None,
                    "overdue_percentage": get_loan_portfolio.overdue_percentage and get_loan_portfolio.overdue_percentage or None,
                    "credit_account_balance": get_loan_portfolio.credit_account_balance and get_loan_portfolio.credit_account_balance or None,
                    "overdue_balance": get_loan_portfolio.overdue_balance and get_loan_portfolio.overdue_balance or None,
                    "overdue_start_date": get_loan_portfolio.overdue_start_date and get_loan_portfolio.overdue_start_date or None,
                    "judicial_balance": get_loan_portfolio.judicial_balance and get_loan_portfolio.judicial_balance or None,
                    "total_overdue": get_loan_portfolio.total_overdue and get_loan_portfolio.total_overdue or None,
                    "quality_class": get_loan_portfolio.quality_class and get_loan_portfolio.quality_class or None,
                    "reserve_balance": get_loan_portfolio.reserve_balance and get_loan_portfolio.reserve_balance or None,
                    "security_valuation": get_loan_portfolio.security_valuation and get_loan_portfolio.security_valuation or None,
                    "loan_security": get_loan_portfolio.loan_security and get_loan_portfolio.loan_security or None,
                    "security_description": get_loan_portfolio.security_description and get_loan_portfolio.security_description or None,
                    "funds_sources": get_loan_portfolio.funds_sources and get_loan_portfolio.funds_sources or None,
                    "lending_type": get_loan_portfolio.lending_type and get_loan_portfolio.lending_type or None,
                    "loan_goal": get_loan_portfolio.loan_goal and get_loan_portfolio.loan_goal or None,
                    "client_parent_org": get_loan_portfolio.client_parent_org and get_loan_portfolio.client_parent_org or None,
                    "loan_industry": get_loan_portfolio.loan_industry and get_loan_portfolio.loan_industry or None,
                    "client_industry": get_loan_portfolio.client_industry and get_loan_portfolio.client_industry or None,
                    "credit_rating": get_loan_portfolio.credit_rating and get_loan_portfolio.credit_rating or None,
                    "cb_chairman": get_loan_portfolio.cb_chairman and get_loan_portfolio.cb_chairman or None,
                    "client_address": get_loan_portfolio.client_address and get_loan_portfolio.client_address or None,
                    "contract_uid": get_loan_portfolio.contract_uid and get_loan_portfolio.contract_uid or None,
                    "inn_passport": get_loan_portfolio.inn_passport and get_loan_portfolio.inn_passport or None,
                    "balance_interest_offbalance": get_loan_portfolio.balance_interest_offbalance and get_loan_portfolio.balance_interest_offbalance or None,
                    "overdue_balance_interest_offbalance": get_loan_portfolio.overdue_balance_interest_offbalance and get_loan_portfolio.overdue_balance_interest_offbalance or None,
                    "sum_cur_year": get_loan_portfolio.sum_cur_year and get_loan_portfolio.sum_cur_year or None,
                    "repaid_cur_year": get_loan_portfolio.repaid_cur_year and get_loan_portfolio.repaid_cur_year or None,
                    "total_issued": get_loan_portfolio.total_issued and get_loan_portfolio.total_issued or None,
                    "total_repaid": get_loan_portfolio.total_repaid and get_loan_portfolio.total_repaid or None,
                    "loan_purpose_specific": get_loan_portfolio.loan_purpose_specific and get_loan_portfolio.loan_purpose_specific or None,
                    "credit_line_purpose": get_loan_portfolio.credit_line_purpose and get_loan_portfolio.credit_line_purpose or None,
                    "judicial_account": get_loan_portfolio.judicial_account and get_loan_portfolio.judicial_account or None,
                    "judicial_account_writeoff": get_loan_portfolio.judicial_account_writeoff and get_loan_portfolio.judicial_account_writeoff or None,
                    "debt_account": get_loan_portfolio.debt_account and get_loan_portfolio.debt_account or None,
                    "inps": get_loan_portfolio.inps and get_loan_portfolio.inps or None,
                    "birth_date": get_loan_portfolio.birth_date and get_loan_portfolio.birth_date or None,
                    "balance_16309": get_loan_portfolio.balance_16309 and get_loan_portfolio.balance_16309 or None,
                    "balance_16379": get_loan_portfolio.balance_16379 and get_loan_portfolio.balance_16379 or None,
                    "balance_16323": get_loan_portfolio.balance_16323 and get_loan_portfolio.balance_16323 or None,
                    "balance_16325": get_loan_portfolio.balance_16325 and get_loan_portfolio.balance_16325 or None,
                    "balance_16377": get_loan_portfolio.balance_16377 and get_loan_portfolio.balance_16377 or None,
                    "balance_16397": get_loan_portfolio.balance_16397 and get_loan_portfolio.balance_16397 or None,
                    "balance_91501": get_loan_portfolio.balance_91501 and get_loan_portfolio.balance_91501 or None,
                    "balance_91503": get_loan_portfolio.balance_91503 and get_loan_portfolio.balance_91503 or None,
                    "balance_95413": get_loan_portfolio.balance_95413 and get_loan_portfolio.balance_95413 or None,
                    "balance_91809": get_loan_portfolio.balance_91809 and get_loan_portfolio.balance_91809 or None,
                    "checking_account": get_loan_portfolio.checkingAccount and get_loan_portfolio.checkingAccount or None,
                    "current_percent_debt_account": get_loan_portfolio.current_percent_debt_account and get_loan_portfolio.current_percent_debt_account or None,
                    "overdue_loan_interest_account": get_loan_portfolio.overdue_loan_interest_account and get_loan_portfolio.overdue_loan_interest_account or None,
                    "percent_balance_on_overdue_loan": get_loan_portfolio.percent_balance_on_overdue_loan and get_loan_portfolio.percent_balance_on_overdue_loan or None,
                    "interest_overdue_account": get_loan_portfolio.interest_overdue_account and get_loan_portfolio.interest_overdue_account or None,
                    "overdue_debt": get_loan_portfolio.overdue_debt and get_loan_portfolio.overdue_debt or None,
                    "accruedOverDueInterest": get_loan_portfolio.accruedOverDueInterest and get_loan_portfolio.accruedOverDueInterest or None,
                    "date_overdue_percent": get_loan_portfolio.date_overdue_percent and get_loan_portfolio.date_overdue_percent or None,
                    "credit_status": get_loan_portfolio.credit_status and get_loan_portfolio.credit_status or None,
                    "checking_account_balance": get_loan_portfolio.checking_account_balance and get_loan_portfolio.checking_account_balance or None,
                    "loan_product": get_loan_portfolio.loan_product and get_loan_portfolio.loan_product or None,
                    "is_target": loan_prod,
                    "mahalla_name": get_loan_portfolio.mahalla_name and get_loan_portfolio.mahalla_name or None,
                    "borrower_type": get_loan_portfolio.borrower_type and get_loan_portfolio.borrower_type or None,
                    "num_workplaces": get_loan_portfolio.num_workplaces and get_loan_portfolio.num_workplaces or None,
                    "gender_id": get_loan_portfolio.gender_id and get_loan_portfolio.gender.name or None,
                    "status": get_loan_portfolio.status and get_loan_portfolio.loan_status or None}
    return loan_portfolio
    
def user_accept_loan(request, user_id, department, db_session):
    
    if department == DEP.PROBLEM.value:
        accept_problems_case(request, user_id, db_session)
        # user = users.get_user_by_department(6,db_session)
    elif department == DEP.JURIDIC.value:
        accept_juridical_case(request, user_id, db_session)
        # user = users.get_user_by_department(7,db_session)
    else: 
        accept_monitoring_case(request, user_id, db_session)
        # if department == 3:
        #     user = users.get_user_by_department(3,db_session)
        # if department == 4:
        #     user = users.get_user_by_department(4,db_session)
    commit_object(db_session)
    
    return 'OK'



def accept_monitoring_case(request, user_id, db_session):
    loan_case_crud.check_if_loan_case_empty(request.accept, db_session)
    
    for loan_portfolio_id in request.accept:
        task = TaskManager_class()
        new_task = task.create_task_manager_when_user_accept_loan(db_session)
        flush_object(db_session)
        case_data = CreateLoanCase()
        case_data.loan_portfolio_id = loan_portfolio_id
        case_data.main_responsible_id = user_id
        
        new_loan_case = loan_case_crud.create_loan_case_with_append_task(new_task, case_data, db_session)
        new_loan_case_history = LoanCaseHistory(loan_case_id = new_loan_case.id, general_task_id = new_task.general_task_id,
                                                from_user_id = user_id, created_at = datetime.datetime.now(),
                                                message = loan_case_history['accept_loan'],
                                                )
        db_session.add(new_loan_case_history)
    get_loans = db_session.query(Loan_Portfolio).filter(Loan_Portfolio.id.in_(request.accept)).all()
    
    for loan in get_loans:
        loan.is_taken_loan = True
        flush_object(db_session)
        
        

def user_accept_loan_list(request, user_id, department, db_session):
    
    if department == DEP.PROBLEM.value:
        accept_problems_case_v2(request, user_id, db_session)
    #     # user = users.get_user_by_department(6,db_session)
    elif department == DEP.JURIDIC.value:
        accept_juridical_case_v2(request, user_id, db_session)
    #     # user = users.get_user_by_department(7,db_session)
    else: 
        accept_monitoring_case_v2(request, user_id, db_session)
        # if department == 3:
        #     user = users.get_user_by_department(3,db_session)
        # if department == 4:
        #     user = users.get_user_by_department(4,db_session)
    commit_object(db_session)
    
    return 'OK'     


def accept_monitoring_case_v2(request, user_id, db_session):
    loan_case_crud.check_if_loan_case_empty(request.accept, db_session)
    
    for loan_portfolio in request.accept:
        task = TaskManager_class()
        new_task = task.create_task_manager_when_user_accept_loan(db_session)
        flush_object(db_session)
        case_data = CreateLoanCase()
        case_data.loan_portfolio_id = loan_portfolio.loan_portfolio_id
        case_data.main_responsible_id = user_id
        
        new_loan_case = loan_case_crud.create_loan_case_with_append_task(new_task, case_data, db_session)
        new_loan_case_history = LoanCaseHistory(loan_case_id = new_loan_case.id, general_task_id = new_task.general_task_id,
                                                from_user_id = user_id, created_at = datetime.datetime.now(),
                                                message = loan_case_history['accept_loan'],
                                                )
        db_session.add(new_loan_case_history)
        
        monitoring_case = loan_case_crud.appoint_responsible_list_tasks(new_loan_case, db_session)
        
        if loan_portfolio.loan_product is not None:
            get_target_status = db_session.query(loan_product).filter(loan_product.name == loan_portfolio.loan_product).first()
            
            if get_target_status.is_target == 0:
                data = UpdateTaskManagerAccept()
                data.task_manager_id = new_task.id
                task = TaskManager_class(data)
                task.loan_case_task_manager_set_on_work(db_session)
            else:
                target_monitoring_crud.appoint_target_monitoring_list_tasks(monitoring_case.id, 3, user_id, request.second_responsible_id,db_session)
        
        
        
    data = CreateNotification()
    data.from_user_id = user_id
    data.to_user_id = request.second_responsible_id
    data.notification_type = notification_dictionary.notification_type['monitoring']
    data.body = f'Поставлено задач(и): {len(request.accept)} '
    data.url = 'no url'
    notifiaction = Notificaton_class(data)
    notifiaction.create_notification(db_session)
    
    portfolios = []
    for portfolio in request.accept:
        portfolios.append(portfolio.loan_portfolio_id)
    get_loans = db_session.query(Loan_Portfolio).filter(Loan_Portfolio.id.in_(portfolios)).all()
    
    for loan in get_loans:
        loan.is_taken_loan = True
        flush_object(db_session)
        
        
        
        
def accept_problems_case(request, user_id, db_session):
    problems_case_crud.check_if_problems_case_has_no_responsible(request, db_session)
    
    for loan_portfolio_id in request.accept:
        data = UserAcceptedLoanData()
        data.task_manager_id = user_id
        
        task = TaskManager_class(data)
        new_task = task.create_task_manager_when_user_accept_problems(db_session)
        flush_object(db_session)
        
        
        
        problems_case = problems_case_crud.update_problems_case_set_responsible(new_task, loan_portfolio_id, user_id, db_session)
        
        
        
        new_problem_case_history = ProblemsCaseHistory(problems_case_id = problems_case.id, general_task_id = new_task.general_task_id,
                                                from_user_id = user_id, created_at = datetime.datetime.now(),
                                                message = problem_case_history['accept_problem'],
                                                )
        db_session.add(new_problem_case_history)
        
    get_loans = db_session.query(Loan_Portfolio).filter(Loan_Portfolio.id.in_(request.accept)).all()
    
    for loan in get_loans:
        loan.is_taken_problem = True
        flush_object(db_session)



def accept_problems_case_v2(request, user_id, db_session):
    problems_case_crud.check_if_problems_list_case_has_no_responsible(request.accept, db_session)
    
    for loan_porfolio in request.accept:
        
        task = TaskManager_class()
        new_task = task.create_task_manager_when_user_accept_problems(db_session)
        flush_object(db_session)
        
        problems_case = problems_case_crud.update_problems_case_set_responsible(new_task, loan_porfolio.loan_portfolio_id, user_id, db_session)
        
        
        new_problem_case_history = ProblemsCaseHistory(problems_case_id = problems_case.id, general_task_id = new_task.general_task_id,
                                                from_user_id = user_id, created_at = datetime.datetime.now(),
                                                message = problem_case_history['accept_problem'],
                                                )
        db_session.add(new_problem_case_history)
        
        problems_case_crud.appoint_second_responsible_for_problems_monitoring_list(problems_case, user_id, request.second_responsible_id, 13, db_session)
        
        
    data = CreateNotification()
    data.from_user_id = user_id
    data.to_user_id = request.second_responsible_id
    data.notification_type = notification_dictionary.notification_type['problems']
    data.body = f'Поставлено задач(и): {len(request.accept)} '
    data.url = 'no url'
    notifiaction = Notificaton_class(data)
    notifiaction.create_notification(db_session)
    
    
    
    portfolios = []
    for portfolio in request.accept:
        portfolios.append(portfolio.loan_portfolio_id)
    get_loans = db_session.query(Loan_Portfolio).filter(Loan_Portfolio.id.in_(portfolios)).all()
    
    for loan in get_loans:
        loan.is_taken_problem = True
        flush_object(db_session)




def accept_juridical_case(request, user_id, db_session):
    juridical_case_crud.check_if_juridical_case_has_no_responsible(request, db_session)
    
    for loan_case in request.accept:
        
        
        data = UserAcceptedLoanData()
        data.task_manager_id = user_id
        
        task = TaskManager_class(data)
        new_task = task.create_task_manager_when_user_accept_juridical(db_session)
        flush_object(db_session)
        
        juridical_case = juridical_case_crud.update_juridical_case_set_responsible(new_task, loan_case, user_id, db_session)
        
        new_jurudical_case_history = JuridicalCaseHistory(juridical_case_id = juridical_case.id, general_task_id = new_task.general_task_id,
                                                from_user_id = user_id, created_at = datetime.datetime.now(),
                                                message = juridical_case_history['accept_juridical'],
                                                )
        db_session.add(new_jurudical_case_history)
        
    get_loans = db_session.query(Loan_Portfolio).filter(Loan_Portfolio.id.in_(request.accept)).all()
    
    for loan in get_loans:
        loan.is_taken_juridic = True
        flush_object(db_session)
        
        

def accept_juridical_case_v2(request, user_id, db_session):
    juridical_case_crud.check_if_juridical_case_list_has_no_responsible(request.accept, db_session)
    
    for loan_case in request.accept:
        
        
        data = UserAcceptedLoanData()
        data.task_manager_id = user_id
        
        task = TaskManager_class(data)
        new_task = task.create_task_manager_when_user_accept_juridical(db_session)
        flush_object(db_session)
        
        juridical_case = juridical_case_crud.update_juridical_case_set_responsible(new_task, loan_case.loan_portfolio_id, user_id, db_session)
        
        new_jurudical_case_history = JuridicalCaseHistory(juridical_case_id = juridical_case.id, general_task_id = new_task.general_task_id,
                                                from_user_id = user_id, created_at = datetime.datetime.now(),
                                                message = juridical_case_history['accept_juridical'],
                                                )
        db_session.add(new_jurudical_case_history)
        
        
        juridical_case_crud.appoint_responsible_for_juridical_monitoring_list(juridical_case, user_id, request.second_responsible_id, JGT.COORDINATE_DOCUMENTS.value, db_session)
        
        
    portfolios = []
    for portfolio in request.accept:
        portfolios.append(portfolio.loan_portfolio_id)
    get_loans = db_session.query(Loan_Portfolio).filter(Loan_Portfolio.id.in_(portfolios)).all()
    
    for loan in get_loans:
        loan.is_taken_juridic = True
        flush_object(db_session)



        
        
        
        
def close_loan_portfolio(loan_portfolio_id, db_session):
    
    loan_porfolio = db_session.query(Loan_Portfolio).filter(Loan_Portfolio.id == loan_portfolio_id).first()
    loan_porfolio.is_taken_juridic = False
    loan_porfolio.status = 3
    
    commit_object(db_session)