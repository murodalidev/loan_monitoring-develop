import datetime

from app.models.problems_case.non_target_state.non_target_files_model import NonTargetStateFiles
from app.models.problems_case.non_target_state.non_target_letters_model import NonTargetLetters
from app.models.problems_case.non_target_state.non_target_state_model import NonTargetState
from app.models.problems_case.non_target_state.non_target_type_model import NonTargetType
from ....models.brief_case.loan_portfolio import Loan_Portfolio
from ....models.loan_case.loan_case_history_model import LoanCaseHistory
from ....models.problems_case.problems_case_model import ProblemsCase
from ....models.problems_case.problems_case_history import ProblemsCaseHistory
from app.models.problems_case.problem_state_chain_model import ProblemStateChain
from app.models.problems_case.problem_states_model import ProblemStates
from ..task_manager.task_manager_crud import TaskManager_class
from ....common import save_file
from ....common.commit import commit_object, flush_object
from fastapi import HTTPException
from ....common.is_empty import is_empty, is_exists, is_empty_list
from ....schemas.task_manager_schemas import UpdateTaskManagerAccept
from ....schemas.notification_schemas import CreateNotification
from ....models.files.monitoring_files_model import MonitoringFiles
from ..notification.notification_crud import Notificaton_class
from ....common.dictionaries import notification_dictionary
from ....common.dictionaries.task_status_dictionaries import task_status
from ....common.dictionaries.monitoring_case_dictionary import problems_case, letter_status
from ....common.dictionaries.case_history_dictionaries import problem_case_history, loan_case_history
from ....common.dictionaries.general_tasks_dictionary import JGT, MGT, PGT, GTCAT
from ....config.logs_config import info_logger
from .problems_case_crud import check_if_non_target_doesnt_exist
from sqlalchemy.sql import text
from ....models.users.users import Users as user, user_role
from ....models.users.attached_branches import attached_branches
from ....common.dictionaries.from_type import FromType
from ....common.dictionaries.departments_dictionary import DEP, ROLES
from ....models.loan_case.loan_case_model import LoanCase
from ....models.users.users import Users as users_model
from sqlalchemy.orm import aliased
from sqlalchemy import case, and_, or_
from sqlalchemy.sql.expression import cast, extract
from sqlalchemy.sql import func
import sqlalchemy
import base64
from ....models.brief_case.loan_portfolio_schedule import LoanPortfolioSchedule
from ....models.statuses.problems_case_status_model import ProblemsCaseStatus
from ....models.brief_case.directories.bank_mfo import bank_mfo
from ....models.brief_case.directories.local_code import local_code
from ....models.brief_case.directories.client_region import client_region
from ....models.brief_case.directories.currency import currency
from ....models.monitoring_task_manager.task_manager_model import TaskManager
from ....models.brief_case.directories.loan_product import loan_product
from ....services.loan_monitoring.monitoring_case.hybrid_letter import hybrid_letter as hybrid_letter_service
from ....services.monitoring_files import files_crud





def create_problems_non_target(problem_data, department_id, target_files, db_session):
    info_logger.info(f"user with department {department_id} is sending loan to problem")
    info_logger.info(f"data: {problem_data}")
    check_if_non_target_doesnt_exist(problem_data.loan_portfolio_id, db_session)
    is_taken = None
    get_attached_user = None
    if department_id == DEP.KAD.value:
        get_problems_case = db_session.query(ProblemsCase).filter(ProblemsCase.loan_portfolio_id == problem_data.loan_portfolio_id)\
            .join(Loan_Portfolio, Loan_Portfolio.id==ProblemsCase.loan_portfolio_id).filter(Loan_Portfolio.is_taken_problem==True).first()
        if get_problems_case is not None:
            get_problems_case.amount=problem_data.amount
            data = UpdateTaskManagerAccept()
            data.task_manager_id = get_problems_case.task_manager_id
            data.general_task_id = problem_data.general_task_id
            data.task_status = task_status['на проверку']
            task = TaskManager_class(data)
            task.update_task_manager(db_session)
            
            case_history = LoanCaseHistory(loan_case_id = problem_data.case_id, general_task_id = problem_data.general_task_id,
                                                    from_user_id = problem_data.from_user, created_at = datetime.datetime.now(),
                                                    comment = problem_data.comment,
                                                    message = loan_case_history['send_to_problem'],
                                                    )
            db_session.add(case_history)
            
            new_problem_case_history = ProblemsCaseHistory(problems_case_id = get_problems_case.id, general_task_id = MGT.SEND_PORBLEM.value,
                                                from_user_id = problem_data.from_user, created_at = datetime.datetime.now(),
                                                comment = problem_data.comment,
                                                message = problem_case_history['new_loan'],
                                                )
            db_session.add(new_problem_case_history)
            save_file.attach_non_target_files(get_problems_case, target_files, db_session)
            flush_object(db_session)
            
            db_session.execute(text(f"UPDATE loan_portfolio set is_taken_loan=false, is_taken_non_target=true where id = {problem_data.loan_portfolio_id}"))
        else:
            get_portfolio  = db_session.query(Loan_Portfolio).filter(Loan_Portfolio.id==problem_data.loan_portfolio_id).first()
            from_type = FromType.NEW.value
            if get_portfolio.is_taken_kad == True:
                is_taken = 'is_taken_kad'
                from_type = FromType.TYPE_3160.value
            elif get_portfolio.is_taken_business == True:
                is_taken = 'is_taken_business'
                from_type = FromType.TYPE_030.value
            
            get_attached_user = db_session.query(attached_branches).filter(attached_branches.local_code_id == problem_data.local_code_id)\
                .filter(attached_branches.department_id == DEP.PROBLEM.value).first()
            get_second_user = db_session.query(user).filter(user.local_code == problem_data.local_code_id).filter(user.department == DEP.PROBLEM.value)\
                    .join(user_role).filter(user_role.columns.role_id == ROLES.problem_block_filial_admin.value).first()
            
            if get_attached_user is not None and get_second_user is not None:
    
                new_problems = ProblemsCase(loan_portfolio_id = problem_data.loan_portfolio_id,
                                            main_responsible_id = get_attached_user.user_id,
                                            second_responsible_id = get_second_user.id,
                                            from_type_id = from_type,
                                            non_target_amount = problem_data.amount,
                                            deadline_extension_status_id = 1,
                                            problems_case_status_id = problems_case['новый'],
                                            created_at = datetime.datetime.now())
                db_session.add(new_problems)
                flush_object(db_session)
    
                new_problem_case_history = ProblemsCaseHistory(problems_case_id = new_problems.id, general_task_id = MGT.SEND_PORBLEM.value,
                                                from_user_id = problem_data.from_user, created_at = datetime.datetime.now(),
                                                comment = problem_data.comment,
                                                message = problem_case_history['new_loan'],
                                                )
                db_session.add(new_problem_case_history)
                save_file.attach_non_target_files(new_problems, target_files, db_session)
            if is_taken is not None:
                db_session.execute(text(f"UPDATE loan_portfolio set {is_taken}=false, is_taken_loan=false, is_taken_non_target=true, is_taken_problem=true where id = {problem_data.loan_portfolio_id}"))
            else:
                db_session.execute(text(f"UPDATE loan_portfolio set is_taken_loan=false, is_taken_non_target=true, is_taken_problem=true where id = {problem_data.loan_portfolio_id}"))
    flush_object(db_session)
    
    if get_attached_user is not None:
        data = CreateNotification()
        data.from_user_id = problem_data.from_user
        data.to_user_id = get_attached_user.user_id
        
        data.notification_type = notification_dictionary.notification_type['problems']
        data.body = notification_dictionary.notification_body['send_to_problems_non_target']
        data.url = None
        
        notifiaction = Notificaton_class(data)
        notifiaction.create_notification(db_session)
    
    commit_object(db_session)
    info_logger.info(f"user with department {department_id} successfully sent loan to problems case")














def get_all_non_target(size, page, region_id, local_code_id, loan_id, state_chain, client_name, is_target, product_type, client_type, \
    client_code, total_overdue_asc_desc, user, main_responsible, second_responsible, department, db_session):
    
    user_roles = []
    for role in user.roles:
        user_roles.append(role.name)
    main_user = aliased(users_model)
    second_user = aliased(users_model)
    loan_portfolio2 = aliased(Loan_Portfolio)
    loan_portfolio3 = aliased(Loan_Portfolio)
   
            
    period = datetime.date.today()
    
    schedule_sum = case([(func.sum(cast(LoanPortfolioSchedule.summ_red, sqlalchemy.FLOAT)/100)==None, 0)], \
        else_=func.sum(cast(LoanPortfolioSchedule.summ_red, sqlalchemy.FLOAT)/100)).label('schedule_sum')
    
    sub_query_schedule_sum = db_session.query(schedule_sum).join(loan_portfolio2, loan_portfolio2.loan_id==LoanPortfolioSchedule.loan_id, isouter=True)\
        .filter(loan_portfolio2.loan_id==Loan_Portfolio.loan_id)\
        .filter(loan_portfolio2.status==1)\
            .filter(LoanPortfolioSchedule.date_red>=datetime.datetime.now()).scalar_subquery()
        
    sub_query_schedule_date = db_session.query(func.max(LoanPortfolioSchedule.date_red))\
        .join(loan_portfolio3 ,LoanPortfolioSchedule.loan_id == loan_portfolio3.loan_id)\
        .filter(loan_portfolio3.loan_id==Loan_Portfolio.loan_id)\
        .filter(loan_portfolio3.status==1).scalar_subquery()
    main_user_case = case([(ProblemsCase.main_responsible_id == user.id, second_user.full_name)], else_=None).label("full_name")
    problems_case = db_session.query(ProblemsCase.id,
                                    ProblemsCaseStatus.id.label('problem_status_id'),
                                    ProblemsCaseStatus.name.label('problem_status_name'),
                                    LoanCase.id.label("loan_case_id"),
                                    LoanCase.monitoring_case_id.label("monitoring_case_id"),
                                    ProblemStates.name.label('state_chain_name'),
                                    main_user_case,
                                    ProblemsCase.main_responsible_id,
                                    ProblemsCase.second_responsible_id,
                                    Loan_Portfolio.id.label('loan_portfolio_id'),
                                    Loan_Portfolio.loan_id,
                                    Loan_Portfolio.client_name,
                                    Loan_Portfolio.total_overdue,
                                    Loan_Portfolio.overdue_balance,
                                    Loan_Portfolio.overdue_start_date,
                                    Loan_Portfolio.balance_16377,
                                    Loan_Portfolio.date_overdue_percent,
                                    sub_query_schedule_sum.label('total_overdue_by_graph'),
                                    sub_query_schedule_date.label('max_date_red'),
                                    client_region.name.label('region'),
                                    local_code.code.label('local_code'),
                                    currency.code.label('currency_code'),
                                    TaskManager.general_task_id,
                                    ProblemsCase.non_target_amount,
                                    ProblemsCase.created_at
                            )\
                .join(Loan_Portfolio, ProblemsCase.loan_portfolio_id == Loan_Portfolio.id, isouter=False)\
                .join(LoanCase, LoanCase.loan_portfolio_id == ProblemsCase.loan_portfolio_id)\
                .join(TaskManager, ProblemsCase.task_manager_id == TaskManager.id, isouter=True)\
                .join(ProblemsCaseStatus, ProblemsCase.problems_case_status_id == ProblemsCaseStatus.id, isouter=True)\
                .join(ProblemStateChain, ProblemStateChain.loan_id == Loan_Portfolio.loan_id, isouter = True)\
                .join(ProblemStates, ProblemStates.id == ProblemStateChain.last_state_id, isouter = True)\
                .join(main_user, ProblemsCase.main_responsible_id == main_user.id, isouter=True)\
                .join(second_user, ProblemsCase.second_responsible_id == second_user.id, isouter=True)\
                .join(client_region, Loan_Portfolio.client_region == client_region.id, isouter=True)\
                .join(local_code, Loan_Portfolio.local_code_id == local_code.id, isouter=True)\
                    .join(currency, Loan_Portfolio.currency_id == currency.id, isouter=True)\
                .filter(Loan_Portfolio.status == 1)\
                        .filter(Loan_Portfolio.is_taken_non_target == True)\
                            
                        
                
                 
    if region_id is not None:
        problems_case = problems_case.filter(Loan_Portfolio.client_region == region_id)
    
    
    
    if loan_id is not None or client_name is not None:
        problems_case = problems_case.filter(or_(cast(Loan_Portfolio.loan_id, sqlalchemy.Text).like(f'{loan_id}%'), Loan_Portfolio.client_name.ilike(f'%{client_name}%')))
    
    
    if is_target is not None:
        problems_case = problems_case.filter(loan_product.name == Loan_Portfolio.loan_product)\
        .filter(loan_product.is_target == is_target)
    
    if user.local_code != 380:
        if 'superviser' in user_roles:
            local_code_id = user.local_code
        else:
            problems_case = problems_case.filter(ProblemsCase.second_responsible_id == user.id)
    if main_responsible is not None:
        if 'main_superviser' in user_roles or 'main_superviser_problem' in user_roles:
            problems_case = problems_case.filter(ProblemsCase.main_responsible_id == main_responsible)
    
    
    if second_responsible is not None:
        problems_case = problems_case.filter(ProblemsCase.second_responsible_id == second_responsible)
    
    
    if state_chain is not None:
        problems_case = problems_case.filter(ProblemStates.id == state_chain)
        
    
    if local_code_id is not None:
        problems_case = problems_case.filter(Loan_Portfolio.local_code_id == local_code_id)
    
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
        
            
    problems_case = problems_case.order_by(Loan_Portfolio.overdue_balance.asc(),Loan_Portfolio.balance_16377.asc())
        
    count = problems_case.count()
    problems_case = problems_case.limit(size).offset((page-1)*size).all()
    
    problems_case_list = []
    
    for problem in problems_case:
        
        get_schedules = db_session.execute(text(f'''
                                               select * from loan_portfolio_schedule where loan_id = {problem.loan_id} order by date_red
                                               ''')).fetchall()
        
        if get_schedules[0].date_red > datetime.datetime.now():
            repayment_date = get_schedules[0].date_red
            recommended_amount = get_schedules[0].summ_red
        elif get_schedules[-1].date_red < datetime.datetime.now():
            repayment_date = get_schedules[-1].date_red
            recommended_amount = get_schedules[-1].summ_red
        else:
            for schedule in get_schedules:
                if period.year == schedule.date_red.year and period.month == schedule.date_red.month:
                    repayment_date = schedule.date_red
                    recommended_amount = schedule.summ_red
        
        
        recommended_amount = recommended_amount and float(recommended_amount)/100 or None
        loan_client = problem.loan_id
        if problem.client_name is not None:
            loan_client = str(problem.loan_id) +' : '+ problem.client_name
        total_overdue = 0
        total_overdue_by_graph = 0
        if problem.total_overdue is not None and  problem.total_overdue !='0':
            total_overdue = problem.total_overdue
        if problem.total_overdue_by_graph is not None and problem.total_overdue_by_graph!=0:
            total_overdue_by_graph = problem.total_overdue_by_graph/100
        if float(total_overdue) < total_overdue_by_graph:
            recommended_amount = 0
            
            
        problems_case_list.append({"id":problem.id,
                                   'state_chain_name':problem.state_chain_name,
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
                                                  "date_overdue_percent": problem.date_overdue_percent,
                                                  "total_overdue_by_graph": problem.total_overdue_by_graph
                                                  },
                               "monitoring_case_id":problem.monitoring_case_id,
                               "loan_portfolio_schedule": {
                                   "repayment_date": repayment_date,
                                   "recommended_amount":recommended_amount,
                                   "currency_code":problem.currency_code
                               },
                               "responsible": {"full_name":problem.full_name},
                               "non_target_amount":float(problem.non_target_amount!=None and problem.non_target_amount or 0),
                               "main_responsible": problem.main_responsible_id,
                               "second_responsible": problem.second_responsible_id,
                               "case_status": {"id": problem.problem_status_id,
                                               "name": problem.problem_status_name},
                               "created_at":problem.created_at})
    
    return {"items": problems_case_list,
            "total":count,
            "page":page,
            "size":size} 






def send_letter_to_non_target(request, file_path, db_session):
    get_hybrid_letter = db_session.query(NonTargetLetters).filter(NonTargetLetters.problems_case_id == request.problems_case_id).first()
    
    
    if get_hybrid_letter is None:
        get_hybrid_letter = NonTargetLetters(problems_case_id = request.problems_case_id,
                                            letter_receiver_type_id = 1,
                                            letter_status_id = letter_status['новый'],
                                            letter_url = file_path[0]['name'],
                                            created_at = datetime.datetime.now())
        db_session.add(get_hybrid_letter)
        flush_object(db_session)
        
        result = hybrid_letter_service.handleData(1, get_hybrid_letter.id)
        if result == 0:
            info_logger.info(f'borrower type has not found')
            get_hybrid_letter.error_comment = 'Отсутствует тип клиента.'
            get_hybrid_letter.letter_status_id = letter_status['ошибка']
            flush_object(db_session)
        else:
            get_hybrid_letter.letter_post_id = result['letter_post_id']
            get_hybrid_letter.post_id = result['post_id']
            flush_object(db_session)
            
    elif  get_hybrid_letter.letter_status_id == letter_status['новый']:
        
        result = hybrid_letter_service.handleData(1, get_hybrid_letter.id)
        
        get_hybrid_letter.letter_post_id = result['letter_post_id']
        get_hybrid_letter.post_id = result['post_id']
        get_hybrid_letter.updated_at = datetime.datetime.now()
        flush_object(db_session)
    
    if get_hybrid_letter.letter_status_id == letter_status['отправлен']:
        raise HTTPException(status_code=403, detail='Почта уже отправлена.')
    
    with open(file_path[0]['name'], "rb") as pdf_file:
            base64_pdf = base64.b64encode(pdf_file.read()).decode()
    
    hybrid_letter_service.send_letter_to_pochtampt_from_non_target(request, get_hybrid_letter, base64_pdf, db_session) 
    commit_object(db_session)
    # bytes = base64.b64decode(result['base_64'], validate=True)

    # f = open('project_files/letter_files/file.pdf', 'wb')
    # f.write(bytes)
    # f.close()
    
    return {"file_base64":base64_pdf,
            "letter_status": get_hybrid_letter.letter_status_id}
    
    
    
    

def get_letter_by_problems_case_id(problems_case_id, db_session):
    
    hybrid_letter = db_session.query(NonTargetLetters).filter(NonTargetLetters.problems_case_id == problems_case_id).first()
    letters = {}
    
    if hybrid_letter is not None:
        letters = {"id": hybrid_letter.id,
                    "post_id": hybrid_letter.post_id,
                    "letter_url":hybrid_letter.letter_url,
                    "letter_status":hybrid_letter.letter_status_id and hybrid_letter.status,
                    "send_date": hybrid_letter.send_date,
                    "error_comment":hybrid_letter.error_comment,
                    "created_at": hybrid_letter.created_at,
                    "updated_at": hybrid_letter.updated_at}
        
    return letters  










def upload_non_target_state_files(request, file_path, db_session):
    non_target_state_data = db_session.query(NonTargetState).filter(NonTargetState.problems_case_id == request.problems_case_id)\
        .filter(NonTargetState.type_id == request.non_target_type_id).first()
    
    if non_target_state_data is None:
        
        non_target_state_data = NonTargetState(problems_case_id = request.problems_case_id,
                                    type_id = request.non_target_type_id and request.non_target_type_id or None,
                                    created_at = datetime.datetime.now()
                                    )
    
        db_session.add(non_target_state_data)
        flush_object(db_session)
        non_target_state_data.problem_case.updated_at = datetime.datetime.now()
        info_logger.info("user %s required 'upload_non_target_state_files' method", request.from_user)
        info_logger.info("user %s sent files: %s", request.from_user, file_path)
    
        for file in file_path:
            new_non_target_state_file = NonTargetStateFiles(non_target_state_id = non_target_state_data.id,
                                    file_url = file['name'],
                                    created_at =  datetime.datetime.now())
            db_session.add(new_non_target_state_file)
            commit_object(db_session)
    
    commit_object(db_session)
    
    return "OK"




def get_non_target_state(problems_case_id, non_target_type_id, db_session):
    
    non_target_states = db_session.query(NonTargetState).filter(NonTargetState.problems_case_id == problems_case_id)\
        .filter(NonTargetState.type_id == non_target_type_id).all()
    states = []
    if non_target_states is not None:
        for non_target_state in  non_target_states:
            
            states = {"id": non_target_state.id,
                        "problems_case_id": non_target_state.problems_case_id,
                        "type":non_target_state.type_id and non_target_state.type or None,
                        "created_at": non_target_state.created_at,
                        "updated_at": non_target_state.updated_at,
                        "files": non_target_state.files}
        return states  






def get_non_target_state_types(db_session):
    
    non_target_types = db_session.query(NonTargetType).order_by(NonTargetType.id.asc()).all()
    types = []
    
    for non_target_type in non_target_types:
        types.append({"id": non_target_type.id,
                    "name": non_target_type.name,
                    "code":non_target_type.code,
                    })
        
    return types