import datetime
from ....models.loan_case.loan_case_model import LoanCase
from ....models.juridical_case.juridical_case_model import JuridicalCase
from ....models.juridical_case.juridical_intended_overdue_model import JuridicalIntendedOverdue
from ....models.statuses.intended_overdue_type_model import IntendedOverdueType
from ....models.juridical_case.overdue_result_model import OverdueResult
from ....models.problems_case.problems_case_model import ProblemsCase
from ....models.brief_case.loan_portfolio import Loan_Portfolio
from ....models.loan_case.loan_case_history_model import LoanCaseHistory
from ....models.problems_case.problems_case_history import ProblemsCaseHistory
from ....models.juridical_case.juridical_case_history_model import JuridicalCaseHistory
from ....schemas.juridical_case_schemas import JuridicalCaseAppointTask
from ..general_tasks import general_tasks_crud
from ....services.loan_monitoring.loan_porfolio import loan_portfolio_list
from ..task_manager.task_manager_crud import TaskManager_class
from ....common.commit import commit_object, flush_object
from ....common.is_empty import is_empty, is_exists
from ....schemas.task_manager_schemas import UpdateTaskManagerSetResponsible, UpdateTaskManagerClose,UpdateTaskManagerAccept
from ....schemas.task_manager_schemas import UpdateTaskManagerSendToCheck
from ....schemas.notification_schemas import CreateNotification
from ..notification.notification_crud import Notificaton_class
from  app.services.users.users_crud import Users as users
from ....common.dictionaries import notification_dictionary
from ....common.dictionaries.task_status_dictionaries import task_status
from ....common.dictionaries.case_history_dictionaries import problem_case_history, loan_case_history, juridical_case_history
from ....common.dictionaries.monitoring_case_dictionary import juridic_case, problems_case
from ....models.files.monitoring_files_model import MonitoringFiles
from ....common.dictionaries.departments_dictionary import DEP
from ....common.dictionaries.general_tasks_dictionary import JGT, MGT, PGT, GTCAT
import logging
logger = logging.getLogger(__name__)



def send_to_juridical(request, department, file_path, db_session):
    logger.info(f"user with department {department} is sending loan to juridical")
    logger.info(f"data: {request}")
    check_if_juridical_case_has_not_set(request.loan_portfolio_id, db_session)
    if department == DEP.PROBLEM.value:
        case = db_session.query(ProblemsCase).filter(ProblemsCase.id ==request.case_id).first()
        data = UpdateTaskManagerAccept()
        data.task_manager_id = case.task_manager_id
        data.general_task_id = request.general_task_id
        data.task_status = task_status['на проверку']
        task = TaskManager_class(data)
        task.update_task_manager(db_session)
        
        case_history = ProblemsCaseHistory(problems_case_id = case.id, general_task_id = request.general_task_id,
                                                from_user_id = request.from_user, created_at = datetime.datetime.now(),
                                                comment = request.comment,
                                                message = problem_case_history['send_to_juridical'],
                                                )
        db_session.add(case_history)
        flush_object(db_session)
        for file in file_path:
            new_file = MonitoringFiles(file_url = file['name'], created_at = datetime.now(),
                                   ftype = file['type_code'])
            db_session.add(new_file)
            flush_object(db_session)
            case_history.files.append(new_file)
            db_session.add(case_history)
        
    else:
        case = db_session.query(LoanCase).filter(LoanCase.id ==request.case_id).first()
        data = UpdateTaskManagerAccept()
        data.task_manager_id = case.task_manager_id
        data.general_task_id = request.general_task_id
        data.task_status = task_status['на проверку']
        task = TaskManager_class(data)
        task.update_task_manager(db_session)
        
        case_history = LoanCaseHistory(loan_case_id = case.id, general_task_id = request.general_task_id,
                                                from_user_id = request.from_user, created_at = datetime.datetime.now(),
                                                comment = request.comment,
                                                message = loan_case_history['send_to_juridical'],
                                                )
        db_session.add(case_history)
        flush_object(db_session)
        for file in file_path:
            new_file = MonitoringFiles(file_url = file['name'], created_at = datetime.now(),
                                   ftype = file['type_code'])
            db_session.add(new_file)
            flush_object(db_session)
            case_history.files.append(new_file)
            db_session.add(case_history)
        
        
   
    new_juridical = JuridicalCase(loan_portfolio_id = request.loan_portfolio_id,
                                  from_user_id = request.from_user,
                                  intended_overdue_type_id = request.intended_overdue_type_id,
                                  juridical_case_status_id = juridic_case['новый'],
                                  created_at = datetime.datetime.now())
    db_session.add(new_juridical)
    flush_object(db_session)
    
    new_jurudical_case_history = JuridicalCaseHistory(juridical_case_id = new_juridical.id, general_task_id = 19,
                                                from_user_id = request.from_user, created_at = datetime.datetime.now(),
                                                comment = request.comment,
                                                message = juridical_case_history['new_loan'],
                                                )
    db_session.add(new_jurudical_case_history)
    
    flush_object(db_session)
    for file in case_history.files:
        new_jurudical_case_history.files.append(file)
        db_session.add(new_jurudical_case_history)
        new_juridical.files.append(file)
        db_session.add(new_juridical)
    
    data = CreateNotification()
    data.from_user_id = request.from_user
    data.to_user_id = None
    
    data.notification_type = notification_dictionary.notification_type['juridical']
    data.body = notification_dictionary.notification_body['send_to_juridical']
    data.url = None
    
    notifiaction = Notificaton_class(data)
    notifiaction.create_notification(db_session)
    
    user = users.get_user_by_department(DEP.JURIDIC.value,db_session)
    
    commit_object(db_session)
    logger.info(f"user with department {department} successfully sent loan to juridical case")
    
    return user



def send_to_juridical_after_accept_target(request, department, file_path, db_session):
    logger.info(f"user with department {department} is sending loan to juridical")
    logger.info(f"data: {request}")
    check_if_juridical_case_has_not_set(request.loan_portfolio_id, db_session)
    if department == DEP.PROBLEM.value:
        case = db_session.query(ProblemsCase).filter(ProblemsCase.id ==request.case_id).first()
        data = UpdateTaskManagerAccept()
        data.task_manager_id = case.task_manager_id
        data.general_task_id = request.general_task_id
        data.task_status = task_status['на проверку']
        task = TaskManager_class(data)
        task.update_task_manager(db_session)
        
        case_history = ProblemsCaseHistory(problems_case_id = case.id, general_task_id = request.general_task_id,
                                                from_user_id = request.from_user, created_at = datetime.datetime.now(),
                                                comment = request.comment,
                                                message = problem_case_history['send_to_juridical'],
                                                )
        db_session.add(case_history)
        flush_object(db_session)
        
    else:
        case = db_session.query(LoanCase).filter(LoanCase.id ==request.case_id).first()
        data = UpdateTaskManagerAccept()
        data.task_manager_id = case.task_manager_id
        data.general_task_id = request.general_task_id
        data.task_status = task_status['на проверку']
        task = TaskManager_class(data)
        task.update_task_manager(db_session)
        
        case_history = LoanCaseHistory(loan_case_id = case.id, general_task_id = request.general_task_id,
                                                from_user_id = request.from_user, created_at = datetime.datetime.now(),
                                                comment = request.comment,
                                                message = loan_case_history['send_to_juridical'],
                                                )
        db_session.add(case_history)
        flush_object(db_session)
        
        
   
    new_juridical = JuridicalCase(loan_portfolio_id = request.loan_portfolio_id,
                                  from_user_id = request.from_user,
                                  intended_overdue_type_id = request.intended_overdue_type_id,
                                  juridical_case_status_id = juridic_case['новый'],
                                  created_at = datetime.datetime.now())
    db_session.add(new_juridical)
    flush_object(db_session)
    
    new_jurudical_case_history = JuridicalCaseHistory(juridical_case_id = new_juridical.id, general_task_id = JGT.COORDINATE_DOCUMENTS.value,
                                                from_user_id = request.from_user, created_at = datetime.datetime.now(),
                                                comment = request.comment,
                                                message = juridical_case_history['new_loan'],
                                                )
    db_session.add(new_jurudical_case_history)
    
    flush_object(db_session)
    for file in file_path:
        flush_object(db_session)
        new_jurudical_case_history.files.append(file)
        db_session.add(new_jurudical_case_history)
        new_juridical.files.append(file)
        db_session.add(new_juridical)
    
    data = CreateNotification()
    data.from_user_id = request.from_user
    data.to_user_id = None
    
    data.notification_type = notification_dictionary.notification_type['juridical']
    data.body = notification_dictionary.notification_body['send_to_juridical']
    data.url = None
    
    notifiaction = Notificaton_class(data)
    notifiaction.create_notification(db_session)
    
    flush_object(db_session)
    logger.info(f"user with department {department} successfully sent loan to juridical case")
    
    return {"OK"}











def reply_to_new_juridical_case(request, file_path, db_session):
    logger.info(f"juridical user is replying to new loan case.")
    logger.info(f"data: {request}")
    
    get_jur_case = db_session.query(JuridicalCase).filter(JuridicalCase.loan_portfolio_id == request.loan_portfolio_id)\
        .filter(JuridicalCase.juridical_case_status_id == juridic_case['новый']).first()
    
    data = UpdateTaskManagerAccept()
    data.task_manager_id = get_jur_case.task_manager_id
    data.task_status = task_status['ожидание_ответственного']
    task = TaskManager_class(data)
    get_task = task.update_task_manager(db_session)
    
    if get_jur_case.from_user.department == DEP.PROBLEM.value:
        case = db_session.query(ProblemsCase).filter(ProblemsCase.loan_portfolio_id == request.loan_portfolio_id)\
            .filter(ProblemsCase.problems_case_status_id == problems_case['новый']).first()
        
        data = UpdateTaskManagerAccept()
        data.task_manager_id = case.task_manager_id
        data.task_status = task_status['впроцессе']
        task = TaskManager_class(data)
        task.update_task_manager(db_session)
        
        case_history = ProblemsCaseHistory(problems_case_id = case.id, 
                                                    general_task_id = PGT.SEND_JURIDIC.value,
                                                    from_user_id = request.from_user, 
                                                    created_at = datetime.datetime.now(),
                                                    to_user_id = case.main_responsible_id,
                                                    comment = request.comment,
                                                    message = problem_case_history['reply_from_juridical'],
                                                    )
        db_session.add(case_history)
        flush_object(db_session)
        for file in file_path:
            new_file = MonitoringFiles(file_url = file['name'], created_at = datetime.now(),
                                   ftype = file['type_code'])
            db_session.add(new_file)
            flush_object(db_session)
            case_history.files.append(new_file)
            db_session.add(case_history)
            
        case_type = 'problems'
        
    else:
        case = db_session.query(LoanCase).filter(LoanCase.loan_portfolio_id == request.loan_portfolio_id).first()
        
        data = UpdateTaskManagerAccept()
        data.task_manager_id = case.task_manager_id
        data.task_status = task_status['впроцессе']
        task = TaskManager_class(data)
        task.update_task_manager(db_session)
        
        
        case_history = LoanCaseHistory(loan_case_id = case.id, general_task_id = MGT.SEND_JURIDIC.value,
                                                from_user_id = request.from_user, created_at = datetime.datetime.now(),
                                                to_user_id = case.main_responsible_id,
                                                comment = request.comment,
                                                message = loan_case_history['reply_from_juridical'],
                                                )
        db_session.add(case_history)
        flush_object(db_session)
        for path in file_path:
            new_file = MonitoringFiles(file_url = path, created_at = datetime.datetime.now())
            db_session.add(new_file)
            flush_object(db_session)
            case_history.files.append(new_file)
            db_session.add(case_history)
        case_type = 'monitoring'
    data = CreateNotification()
    data.from_user_id = request.from_user
    data.to_user_id = request.to_user
    
    data.notification_type = notification_dictionary.notification_type[case_type]
    data.body = notification_dictionary.notification_body['new_reply_from_juridical']
    data.url = f'{case.loan_portfolio_id}'+':'+ f'{case.id}'
    
    notifiaction = Notificaton_class(data)
    notifiaction.create_notification(db_session)
    
    

    new_jurudical_case_history = JuridicalCaseHistory(juridical_case_id = request.juridical_case_id, general_task_id = request.general_task_id,
                                                from_user_id = request.from_user, created_at = datetime.datetime.now(),
                                                comment = request.comment,
                                                to_user_id = case.main_responsible_id,
                                                message = juridical_case_history['reply_to_new_loan'],
                                                )
    db_session.add(new_jurudical_case_history)
    
    flush_object(db_session)
    for file in case_history.files:
        new_jurudical_case_history.files.append(file)
        db_session.add(new_jurudical_case_history)
        get_jur_case.files.append(file)
        db_session.add(get_jur_case)
    commit_object(db_session)
    logger.info(f"juridical user is successfully replied.")
    return 'OK'



def accept_or_rework(request, db_session):
    logger.info(f"juridical user is accepting or sending to rework.")
    logger.info(f"data: {request}")
    get_jur_case = db_session.query(JuridicalCase).filter(JuridicalCase.id == request.juridical_case_id)\
        .filter(JuridicalCase.juridical_case_status_id == juridic_case['новый']).first()
    
    if get_jur_case.from_user.department == DEP.PROBLEM.value:
        if request.type:
            get_jur_case.juridical_case_status_id = juridic_case['в процессе']
            data = UpdateTaskManagerClose()
            data.task_manager_id = request.task_manager_id
            data.task_status = task_status['завершено']
            task = TaskManager_class(data)
            task.update_task_manager(db_session)
            
            
            new_jurudical_case_history = JuridicalCaseHistory(juridical_case_id = request.juridical_case_id, general_task_id = request.general_task_id,
                                                        from_user_id = request.from_user, created_at = datetime.datetime.now(),
                                                        message = juridical_case_history['apply'],
                                                        )
            db_session.add(new_jurudical_case_history)
            
            case = db_session.query(ProblemsCase).filter(ProblemsCase.loan_portfolio_id == request.loan_portfolio_id)\
                .filter(ProblemsCase.problems_case_status_id == problems_case['новый']).first()
            
            new_problems_case_history = ProblemsCaseHistory(problems_case_id = case.id, 
                                                        general_task_id = PGT.SEND_JURIDIC,
                                                        from_user_id = request.from_user, 
                                                        created_at = datetime.datetime.now(),
                                                        to_user_id = case.main_responsible_id,
                                                        comment = request.comment,
                                                        message = problem_case_history['apply'],
                                                        )
            db_session.add(new_problems_case_history)

            data = UpdateTaskManagerClose()
            data.task_manager_id = case.task_manager_id
            data.task_status = task_status['завершено']
            task = TaskManager_class(data)
            task.update_task_manager(db_session)
            
            case_type = 'problems'
            data = CreateNotification()
            data.from_user_id = request.from_user
            data.to_user_id = request.to_user
            
            data.notification_type = notification_dictionary.notification_type[case_type]
            data.body = notification_dictionary.notification_body['new_reply_from_juridical']
            data.url = f'{case.loan_portfolio_id}'+':'+ f'{case.id}'
            
            notifiaction = Notificaton_class(data)
            notifiaction.create_notification(db_session)
            
            
            commit_object(db_session)
            logger.info(f"juridical user accepted task from problems user.")
        else:
            data = UpdateTaskManagerClose()
            data.task_manager_id = request.task_manager_id
            data.task_status = task_status['переделать']
            task = TaskManager_class(data)
            task.update_task_manager(db_session)
            
            juridical_file_delete_last_files(request.juridical_case_id,request.general_task_id,db_session)
            
            new_jurudical_case_history = JuridicalCaseHistory(juridical_case_id = request.juridical_case_id, general_task_id = request.general_task_id,
                                                        from_user_id = request.from_user, created_at = datetime.datetime.now(),
                                                        message = juridical_case_history['rework'],
                                                        )
            db_session.add(new_jurudical_case_history)
            
            case = db_session.query(ProblemsCase).filter(ProblemsCase.loan_portfolio_id == request.loan_portfolio_id)\
                .filter(ProblemsCase.problems_case_status_id == problems_case['новый']).first()
            
            new_problems_case_history = ProblemsCaseHistory(problems_case_id = case.id, 
                                                        general_task_id = PGT.SEND_JURIDIC.value,
                                                        from_user_id = request.from_user, 
                                                        created_at = datetime.datetime.now(),
                                                        to_user_id = case.main_responsible_id,
                                                        comment = request.comment,
                                                        message = problem_case_history['rework'],
                                                        )
            db_session.add(new_problems_case_history)

            data = UpdateTaskManagerClose()
            data.task_manager_id = case.task_manager_id
            data.task_status = task_status['переделать']
            task = TaskManager_class(data)
            task.update_task_manager(db_session)
            
            case_type = 'problems'
            data = CreateNotification()
            data.from_user_id = request.from_user
            data.to_user_id = request.to_user
            
            data.notification_type = notification_dictionary.notification_type[case_type]
            data.body = notification_dictionary.notification_body['new_reply_from_juridical']
            data.url = f'{case.loan_portfolio_id}'+':'+ f'{case.id}'
            
            notifiaction = Notificaton_class(data)
            notifiaction.create_notification(db_session)
            
            
            commit_object(db_session)
            logger.info(f"juridical user send task from problem user to rework.")
    else:
        if request.type:
            get_jur_case.juridical_case_status_id = juridic_case['в процессе']
            data = UpdateTaskManagerClose()
            data.task_manager_id = request.task_manager_id
            data.task_status = task_status['завершено']
            task = TaskManager_class(data)
            task.update_task_manager(db_session)
            
            
            new_jurudical_case_history = JuridicalCaseHistory(juridical_case_id = request.juridical_case_id, general_task_id = request.general_task_id,
                                                        from_user_id = request.from_user, created_at = datetime.datetime.now(),
                                                        message = juridical_case_history['apply'],
                                                        )
            db_session.add(new_jurudical_case_history)
            
            case = db_session.query(LoanCase).filter(LoanCase.loan_portfolio_id == request.loan_portfolio_id).first()
            
            new_loan_case_history = LoanCaseHistory(loan_case_id = case.id, 
                                                        general_task_id = MGT.SEND_JURIDIC.value,
                                                        from_user_id = request.from_user, 
                                                        created_at = datetime.datetime.now(),
                                                        to_user_id = case.main_responsible_id,
                                                        comment = request.comment,
                                                        message = loan_case_history['apply'],
                                                        )
            db_session.add(new_loan_case_history)

            data = UpdateTaskManagerClose()
            data.task_manager_id = case.task_manager_id
            data.task_status = task_status['завершено']
            task = TaskManager_class(data)
            task.update_task_manager(db_session)
            
            case_type = 'monitoring'
            data = CreateNotification()
            data.from_user_id = request.from_user
            data.to_user_id = request.to_user
            
            data.notification_type = notification_dictionary.notification_type[case_type]
            data.body = notification_dictionary.notification_body['new_reply_from_juridical']
            data.url = f'{case.loan_portfolio_id}'+':'+ f'{case.id}'
            
            notifiaction = Notificaton_class(data)
            notifiaction.create_notification(db_session)
            
            
            commit_object(db_session)
            logger.info(f"juridical user accepted task from monitoring user.")
        else:
            data = UpdateTaskManagerClose()
            data.task_manager_id = request.task_manager_id
            data.task_status = task_status['переделать']
            task = TaskManager_class(data)
            task.update_task_manager(db_session)
            
            juridical_file_delete_last_files(request.juridical_case_id,request.general_task_id,db_session)
            
            new_jurudical_case_history = JuridicalCaseHistory(juridical_case_id = request.juridical_case_id, general_task_id = request.general_task_id,
                                                        from_user_id = request.from_user, created_at = datetime.datetime.now(),
                                                        message = juridical_case_history['rework'],
                                                        )
            db_session.add(new_jurudical_case_history)
            
            case = db_session.query(LoanCase).filter(LoanCase.loan_portfolio_id == request.loan_portfolio_id).first()
            
            new_loan_case_history = LoanCaseHistory(loan_case_id = case.id, 
                                                        general_task_id = MGT.SEND_JURIDIC.value,
                                                        from_user_id = request.from_user, 
                                                        created_at = datetime.datetime.now(),
                                                        to_user_id = case.main_responsible_id,
                                                        comment = request.comment,
                                                        message = loan_case_history['rework'],
                                                        )
            db_session.add(new_loan_case_history)

            data = UpdateTaskManagerClose()
            data.task_manager_id = case.task_manager_id
            data.task_status = task_status['переделать']
            task = TaskManager_class(data)
            task.update_task_manager(db_session)
            
            case_type = 'monitoring'
            data = CreateNotification()
            data.from_user_id = request.from_user
            data.to_user_id = request.to_user
            
            data.notification_type = notification_dictionary.notification_type[case_type]
            data.body = notification_dictionary.notification_body['new_reply_from_juridical']
            data.url = f'{case.loan_portfolio_id}'+':'+ f'{case.id}'
            
            notifiaction = Notificaton_class(data)
            notifiaction.create_notification(db_session)
            
            
            commit_object(db_session)
            logger.info(f"juridical user send task from monitoring user to rework.")
    return "OK"


def appoint_responsible_for_juridical_monitoring(request, db_session):
    logger.info(f"juridical user send is appending second responsible to juridical case")
    logger.info(f"data: {request}")
    juridical_case = check_if_juridical_intended_has_no_responsible(request.juridical_case_id, db_session)
    
    
    juridical_case.second_responsible_id = request.to_user
    juridical_case.updated_at = datetime.datetime.now()
    
    
    data = UpdateTaskManagerSetResponsible()
    data.task_manager_id = juridical_case.task_manager_id
    data.general_task_id = request.general_task_id
    data.task_status = task_status['завершено']
    task = TaskManager_class(data)
    task.update_task_manager(db_session)
    
    
      
    data = CreateNotification()
    data.from_user_id = request.from_user
    data.to_user_id = request.to_user
    data.notification_type = notification_dictionary.notification_type['juridical']
    data.body = notification_dictionary.notification_body['juridical_appoint']
    data.url = f'{juridical_case.loan_portfolio_id}'+':'+ f'{juridical_case.id}'
    
    notifiaction = Notificaton_class(data)
    notifiaction.create_notification(db_session)
    
    
    new_jurudical_case_history = JuridicalCaseHistory(juridical_case_id = juridical_case.id, general_task_id = request.general_task_id,
                                                        from_user_id = request.from_user, created_at = datetime.datetime.now(),
                                                        to_user_id = request.to_user,
                                                        comment = request.comment,
                                                        message = juridical_case_history['appoint_responsible'],
                                                        )
    db_session.add(new_jurudical_case_history)
    
    
    commit_object(db_session)
    logger.info(f"juridical user send is successfully appended second user to juridical case")
    return "OK"





def appoint_responsible_for_juridical_monitoring_list(juridical_case, from_user, second_responsible_id, general_task_id, db_session):
    logger.info(f"juridical user send is appending second responsible to juridical case")
    
    juridical_case.second_responsible_id = second_responsible_id
    juridical_case.updated_at = datetime.datetime.now()
    
    
    data = UpdateTaskManagerSetResponsible()
    data.task_manager_id = juridical_case.task_manager_id
    data.general_task_id = general_task_id
    data.task_status = task_status['на проверку']
    task = TaskManager_class(data)
    task.update_task_manager(db_session)
    
    new_jurudical_case_history = JuridicalCaseHistory(juridical_case_id = juridical_case.id, general_task_id = general_task_id,
                                                        from_user_id = from_user, created_at = datetime.datetime.now(),
                                                        to_user_id = second_responsible_id,
                                                        message = juridical_case_history['appoint_responsible'],
                                                        )
    db_session.add(new_jurudical_case_history)
    
    
    commit_object(db_session)
    logger.info(f"juridical user send is successfully appended second user to juridical case")
    return "OK"










def check_if_juridical_intended_has_no_responsible(juridical_case_id, db_session):#used
    get_juridical_case = db_session.query(JuridicalCase)\
            .filter(JuridicalCase.id == juridical_case_id)\
            .filter(JuridicalCase.second_responsible_id == None).first()
    is_exists(get_juridical_case, 400,f'Juridical case has already appended to second user.')
    return get_juridical_case




def check_if_juridical_case_has_no_responsible(request, db_session):#used
    for accept in request.accept:
        juridical_case = db_session.query(JuridicalCase)\
            .filter(JuridicalCase.loan_portfolio_id == accept)\
            .filter(JuridicalCase.main_responsible_id == None).first()
        is_exists(juridical_case, 400,f'Juridical case has already appended to user.')
        
def check_if_juridical_case_list_has_no_responsible(request, db_session):#used
    portfolios = []
    for portfolio in request:
        portfolios.append(portfolio.loan_portfolio_id)
    
    juridical_case = db_session.query(JuridicalCase)\
        .filter(JuridicalCase.loan_portfolio_id.in_(portfolios and portfolios or ()))\
        .filter(JuridicalCase.main_responsible_id == None).first()
    is_exists(juridical_case, 400,f'Juridical case has already appended to user.')




def check_if_juridical_case_has_not_set(loan_portfolio_id, db_session):#used
    
    juridical_case = db_session.query(JuridicalCase)\
            .filter(JuridicalCase.loan_portfolio_id == loan_portfolio_id)\
            .filter(JuridicalCase.juridical_case_status_id != juridic_case['закрыт']).first()
    is_empty(juridical_case, 400,f'Juridical case has already appended to user.')
        
        
        
        
        
        
def update_juridical_case_set_responsible(new_task, loan_portfolio_id, responsible_id, db_session):#used
    get_juridical_case = db_session.query(JuridicalCase)\
        .filter(JuridicalCase.loan_portfolio_id == loan_portfolio_id)\
            .filter(JuridicalCase.juridical_case_status_id == juridic_case['новый']).first()
    get_juridical_case.main_responsible_id = responsible_id
    get_juridical_case.task_manager_id = new_task.id
    return get_juridical_case


def check_if_juridical_task_has_not_appointed(general_task_id,juridical_case_id, db_session):#used
    juridical_intended = db_session.query(JuridicalIntendedOverdue)\
            .filter(JuridicalIntendedOverdue.juridical_type_id == general_task_id)\
                .filter(JuridicalIntendedOverdue.juridical_case_id == juridical_case_id).first()
    is_empty(juridical_intended, 400,f'Juridical task has already appointed.')
        
        

def update_juridical_case_close(juridical_case_id, db_session):#used
    get_juridical_case = db_session.query(JuridicalCase)\
        .filter(JuridicalCase.id == juridical_case_id).first()
    get_juridical_case.juridical_case_status_id = juridic_case['закрыт']
    return get_juridical_case





def juridical_appoint_tasks(request, db_session):
    logger.info(f"juridical user is appointing task.")
    logger.info(f"data: {request}")
    check_if_juridical_task_has_not_appointed(request.general_task_id, request.juridical_case_id, db_session)
    
    
    data = JuridicalCaseAppointTask()
    data.general_task_id = request.general_task_id
    data.deadline = request.deadline
    
    task = TaskManager_class(data)
    new_task = task.create_task_manager_when_set_juridical_intended_task(db_session)
    
    
    new_juridical_intended = JuridicalIntendedOverdue(juridical_case_id = request.juridical_case_id,
                                                      juridical_type_id = request.general_task_id,
                                                      task_manager_id = new_task.id,
                                                      created_at = datetime.datetime.now())
    db_session.add(new_juridical_intended)
    
    
    
    
    addditional_data = {"dedline":request.deadline}
    
    data = JuridicalCaseAppointTask()
    data.task_manager_id = request.task_manager_id
    data.general_task_id = request.general_task_id
    data.task_status = task_status['начато']
    task = TaskManager_class(data)
    new_task = task.update_task_manager(db_session)
    
    get_juridical_case = db_session.query(JuridicalCase).filter(JuridicalCase.id == request.juridical_case_id).first()
    
    data = CreateNotification()
    data.from_user_id = request.from_user
    data.to_user_id = request.to_user
    
    data.notification_type = notification_dictionary.notification_type['juridical']
    data.body = notification_dictionary.notification_body['appoint_juridical_task']
    data.url = f'{get_juridical_case.loan_portfolio_id}'+':'+ f'{request.juridical_case_id}'
    
    notifiaction = Notificaton_class(data)
    notifiaction.create_notification(db_session)
    
    
    new_jurudical_case_history = JuridicalCaseHistory(juridical_case_id = request.juridical_case_id, general_task_id = request.general_task_id,
                                                        from_user_id = request.from_user, created_at = datetime.datetime.now(),
                                                        to_user_id = request.to_user,
                                                        comment = request.comment,
                                                        message = juridical_case_history['appoint_task'],
                                                        additional_data = addditional_data
                                                        )
    db_session.add(new_jurudical_case_history)
    
    commit_object(db_session)
    logger.info(f"juridical user is successfully appointed task.")
    return "OK"
    
    
    
    
    
    
    
def upload_file_send_results(request, file_path, db_session):
    logger.info(f"juridical user is sending result to main juridical responsible.")
    logger.info(f"data: {request}")
    
    data = UpdateTaskManagerSendToCheck()
    data.task_manager_id = request.task_manager_id
    data.task_status = task_status['на проверку']
    task = TaskManager_class(data)
    updated_task = task.update_task_manager(db_session)
    
    get_juridical_case = db_session.query(JuridicalCase).filter(JuridicalCase.id == request.juridical_case_id).first()
    data = JuridicalCaseAppointTask()
    data.task_manager_id = get_juridical_case.task_manager_id
    data.task_status = task_status['на проверку']
    task = TaskManager_class(data)
    task.update_task_manager(db_session)
    
    get_overdue = db_session.query(JuridicalIntendedOverdue).filter(JuridicalIntendedOverdue.id == request.intended_overdue_id).first()
    get_overdue.overdue_result = request.overdue_result
    get_overdue.updated_at = datetime.datetime.now()
    
    additional_data = {'Результат': request.overdue_result}
    
    get_juridical_case = db_session.query(JuridicalCase).filter(JuridicalCase.id == request.juridical_case_id).first()
    data = CreateNotification()
    data.from_user_id = request.from_user
    data.to_user_id = request.to_user
    data.notification_type = notification_dictionary.notification_type['juridical']
    data.body = notification_dictionary.notification_body['send_to_check_juridic_task']
    data.url = f'{get_juridical_case.loan_portfolio_id}'+':'+ f'{request.juridical_case_id}'
    
    notifiaction = Notificaton_class(data)
    notifiaction.create_notification(db_session)
    
    new_loan_case_history = JuridicalCaseHistory(juridical_case_id = request.juridical_case_id, 
                                            general_task_id = updated_task.general_task_id,
                                            from_user_id = request.from_user, 
                                            to_user_id= request.to_user,
                                            comment = request.comment,
                                            created_at = datetime.datetime.now(),
                                            message = juridical_case_history['send_task_to_chcek'],
                                            additional_data = additional_data
                                                )
    db_session.add(new_loan_case_history)
    
    for file in file_path:
        new_file = MonitoringFiles(file_url = file['name'], created_at = datetime.now(),
                                   ftype = file['type_code'])
        db_session.add(new_file)
        flush_object(db_session)
        new_loan_case_history.files.append(new_file)
        db_session.add(new_loan_case_history)
        get_juridical_case.files.append(new_file)
        db_session.add(get_juridical_case)
    
    
    
    commit_object(db_session)
    logger.info(f"juridical user successfully sent results to main responsible.")
    return "OK"
    
    
def acept_or_rework_task(request, db_session):
    logger.info(f"juridical user is going to accept or send to rework task.")
    logger.info(f"data: {request}")
    #overdue_intended = db_session.query(JuridicalIntendedOverdue).filter(JuridicalIntendedOverdue.id == request.intended_overdue_id).first()
    
    
    if request.result_type:
        additional_data = {'intended_overdue_status': 'согласовано'}
        message = juridical_case_history['accepted']
        body = notification_dictionary.notification_body['accept_juridical_task']
        data = UpdateTaskManagerAccept()
        data.task_manager_id = request.task_manager_id
        data.task_status = task_status['завершено']
        task = TaskManager_class(data)
        updated_task = task.update_task_manager(db_session)
        
        get_juridical_case = db_session.query(JuridicalCase).filter(JuridicalCase.id == request.juridical_case_id).first()
        data = JuridicalCaseAppointTask()
        data.task_manager_id = get_juridical_case.task_manager_id
        data.task_status = task_status['завершено']
        task = TaskManager_class(data)
        task.update_task_manager(db_session)
        
        logger.info(f"juridical user accepted task.")
    else:
        additional_data = {'intended_overdue_status': 'переделать'}
        message = juridical_case_history['rejected']
        body = notification_dictionary.notification_body['rework_juridical_task']
        data = UpdateTaskManagerAccept()
        data.task_manager_id = request.task_manager_id
        data.task_status = task_status['переделать']
        task = TaskManager_class(data)
        updated_task =task.update_task_manager(db_session)
        
        get_juridical_case = db_session.query(JuridicalCase).filter(JuridicalCase.id == request.juridical_case_id).first()
        data = JuridicalCaseAppointTask()
        data.task_manager_id = get_juridical_case.task_manager_id
        data.task_status = task_status['переделать']
        task = TaskManager_class(data)
        task.update_task_manager(db_session)
        
        juridical_file_delete_last_files(request.juridical_case_id, get_juridical_case.task[0].general_task_id, db_session)
        
        logger.info(f"juridical user sent task to rework.")
    
    
    
    data = CreateNotification()
    data.from_user_id = request.from_user 
    data.to_user_id =request.to_user
    data.notification_type = notification_dictionary.notification_type['juridical']
    data.body = body
    data.url = f'{get_juridical_case.loan_portfolio_id}'+':'+ f'{request.juridical_case_id}'
    notifiaction = Notificaton_class(data)
    notifiaction.create_notification(db_session)
    
    new_loan_case_history = JuridicalCaseHistory(juridical_case_id = request.juridical_case_id, 
                                            general_task_id = updated_task.general_task_id,
                                            from_user_id = request.from_user, 
                                            to_user_id= request.to_user,
                                            comment = request.comment,
                                            created_at = datetime.datetime.now(),
                                            message = message,
                                            additional_data = additional_data
                                                )
    db_session.add(new_loan_case_history)
    
    
    
    commit_object(db_session)
    
    return {"OK"}



def return_juridical(request, db_session):
    logger.info(f"juridical is going to return juridical case.")
    logger.info(f"data: {request}")
    juridical_case = update_juridical_case_close(request.juridical_case_id, db_session)
    
    new_loan_case_history = JuridicalCaseHistory(juridical_case_id = request.juridical_case_id, 
                                            general_task_id = request.general_task_id,
                                            from_user_id = request.from_user,
                                            created_at = datetime.datetime.now(),
                                            message = juridical_case_history['returned'],
                                                )
    db_session.add(new_loan_case_history)
    
    data = UpdateTaskManagerClose()
    data.task_manager_id = juridical_case.task_manager_id
    data.general_task_id = request.general_task_id
    data.task_status = task_status['завершено']
    task = TaskManager_class(data)
    task.update_task_manager(db_session)
    
    if juridical_case.from_user.department == DEP.PROBLEM.value:
        case = db_session.query(ProblemsCase).filter(ProblemsCase.loan_portfolio_id == request.loan_portfolio_id)\
            .filter(ProblemsCase.problems_case_status_id == problems_case['новый']).first()
        case.problems_case_status_id = problems_case['закрыт']
        
        loan_portfolio = db_session.query(Loan_Portfolio).filter(Loan_Portfolio.id == request.loan_portfolio_id).first()
        loan_portfolio.is_taken_problem = False
        
        new_problems_case_history = ProblemsCaseHistory(problems_case_id = case.id, 
                                                    general_task_id = PGT.REPAID.value,
                                                    from_user_id = request.from_user, 
                                                    created_at = datetime.datetime.now(),
                                                    to_user_id = case.main_responsible_id,
                                                    message = problem_case_history['return'],
                                                    )
        db_session.add(new_problems_case_history)

        data = UpdateTaskManagerClose()
        data.task_manager_id = case.task_manager_id
        case_type = 'problems'
        task = TaskManager_class(data)
        task.update_task_manager_problems_set_closed(db_session)
        case = db_session.query(LoanCase).filter(LoanCase.loan_portfolio_id == request.loan_portfolio_id).first()
        data = UpdateTaskManagerClose()
        data.task_manager_id = case.task_manager_id
        task = TaskManager_class(data)
        task.update_task_manager_monitoring_set_in_work(db_session)
    else:
        case = db_session.query(LoanCase).filter(LoanCase.loan_portfolio_id == request.loan_portfolio_id).first()
            
        new_loan_case_history = LoanCaseHistory(loan_case_id = case.id, 
                                                    general_task_id = MGT.SEND_JURIDIC,
                                                    from_user_id = request.from_user, 
                                                    created_at = datetime.datetime.now(),
                                                    to_user_id = case.main_responsible_id,
                                                    message = loan_case_history['return'],
                                                    )
        db_session.add(new_loan_case_history)

        data = UpdateTaskManagerClose()
        data.task_manager_id = case.task_manager_id
        case_type = 'monitoring'
        task = TaskManager_class(data)
        task.update_task_manager_monitoring_set_in_work(db_session)
        
    data = CreateNotification()
    data.from_user_id = request.from_user
    data.to_user_id = case.main_responsible_id
    data.notification_type = notification_dictionary.notification_type[case_type]
    data.body = notification_dictionary.notification_body['return_juridical_case']
    data.url = f'{case.loan_portfolio_id}' + ':' + f'{case.id}'
    notifiaction = Notificaton_class(data)
    notifiaction.create_notification(db_session)
    loan_portfolio = db_session.query(Loan_Portfolio).filter(Loan_Portfolio.id == request.loan_portfolio_id).first()
    loan_portfolio.is_taken_juridic = False
        
    commit_object(db_session)
    logger.info(f"juridical returned loan and closed juridical case.")
    return {'to_user_id':case.main_responsible_id}





def finish_juridical(request, db_session):
    logger.info(f"juridical is going to finish juridical case.")
    logger.info(f"data: {request}")
    juridical_case = update_juridical_case_close(request.juridical_case_id, db_session)
    
    new_loan_case_history = JuridicalCaseHistory(juridical_case_id = request.juridical_case_id, 
                                            general_task_id = request.general_task_id,
                                            from_user_id = request.from_user,
                                            created_at = datetime.datetime.now(),
                                            message = juridical_case_history['finished'],
                                                )
    db_session.add(new_loan_case_history)
    
    data = UpdateTaskManagerClose()
    data.task_manager_id = juridical_case.task_manager_id
    data.general_task_id = request.general_task_id
    data.task_status = task_status['завершено']
    task = TaskManager_class(data)
    task.update_task_manager(db_session)
    
    if juridical_case.from_user.department == DEP.PROBLEM.value:
        case = db_session.query(ProblemsCase).filter(ProblemsCase.loan_portfolio_id == request.loan_portfolio_id)\
            .filter(ProblemsCase.problems_case_status_id == problems_case['в процессе']).first()
            
        loan_portfolio = db_session.query(Loan_Portfolio).filter(Loan_Portfolio.id == request.loan_portfolio_id).first()
        loan_portfolio.is_taken_problem = False
        new_problems_case_history = ProblemsCaseHistory(problems_case_id = case.id, 
                                                    general_task_id = PGT.SEND_JURIDIC.value,
                                                    from_user_id = request.from_user, 
                                                    created_at = datetime.datetime.now(),
                                                    to_user_id = case.main_responsible_id,
                                                    message = problem_case_history['finished'],
                                                    )
        db_session.add(new_problems_case_history)

        case_type = 'problems'
    else:
        case = db_session.query(LoanCase).filter(LoanCase.loan_portfolio_id == request.loan_portfolio_id).first()
            
        new_loan_case_history = LoanCaseHistory(loan_case_id = case.id, 
                                                    general_task_id = MGT.SEND_JURIDIC.value,
                                                    from_user_id = request.from_user, 
                                                    created_at = datetime.datetime.now(),
                                                    to_user_id = case.main_responsible_id,
                                                    message = loan_case_history['finished'],
                                                    )
        db_session.add(new_loan_case_history)
        case_type = 'monitoring'
    data = CreateNotification()
    data.from_user_id = request.from_user
    data.to_user_id = case.main_responsible_id
    data.notification_type = notification_dictionary.notification_type[case_type]
    data.body = notification_dictionary.notification_body['finish_juridical_case']
    data.url = f'{case.loan_portfolio_id}' + ':' + f'{case.id}'
    notifiaction = Notificaton_class(data)
    notifiaction.create_notification(db_session)
    
    loan_portfolio_list.close_loan_portfolio(request.loan_portfolio_id, db_session)
    
    commit_object(db_session)
    logger.info(f"juridical finished loan and closed juridical case.")
    return {'to_user_id':case.main_responsible_id}














def get_juridical_case_history(juridical_case_id,general_task_id, db_session):
    logger.info(f"juridical user is requiring juridical case history.")
    logger.info(f"data: juridical_case_id: {juridical_case_id}, general_task_id: {general_task_id}")
    case_history = []
    juridical_case_history = db_session.query(JuridicalCaseHistory).filter(JuridicalCaseHistory.general_task_id == general_task_id)\
        .filter(JuridicalCaseHistory.juridical_case_id == juridical_case_id).all()
    
    if juridical_case_history != []:
        for history in juridical_case_history:
            from_user =  users.get_user_by_id(history.from_user_id, db_session)
            to_user = users.get_user_by_id(history.to_user_id, db_session)
            case_history.append({"id":history.id,
                                "from_user": from_user,
                                "to_user": to_user,
                                "created_at": history.created_at,
                                "updated_at": history.updated_at,
                                "comment": history.comment,
                                "message": history.message,
                                "additional_data": history.additional_data,
                                "files": history.files and history.files})
        
    return case_history



def get_juridical_intended_ocerdue(juridical_case_id, juridical_type_id, db_session):
    logger.info(f"juridical user is requiring juridical intended overdue.")
    logger.info(f"data: juridical_case_id: {juridical_case_id}, juridical_type_id: {juridical_type_id}")
    juridical_intended_overdue = {}
    juridical_intended = db_session.query(JuridicalIntendedOverdue).filter(JuridicalIntendedOverdue.juridical_case_id == juridical_case_id)\
        .filter(JuridicalIntendedOverdue.juridical_type_id == juridical_type_id).first()
    
    
    if juridical_intended is not None:
        juridical_intended_overdue = {"id":juridical_intended.id,
                             "juridical_case_id": juridical_intended.juridical_case_id and juridical_intended.juridical_case_id or None,
                             "juridical_type_id": juridical_intended.juridical_type_id and juridical_intended.juridical_type_id or None,
                             "overdue_result": juridical_intended.overdue_result and juridical_intended.result or None,
                             "created_at": juridical_intended.created_at and juridical_intended.created_at or None,
                             "updated_at": juridical_intended.updated_at and juridical_intended.updated_at or None,
                             "task": juridical_intended.task and  TaskManager_class.get_task_manager_by_id(juridical_intended.task, db_session) or None
                             }
        
    return juridical_intended_overdue








def get_intended_overdue_type(db_session):
    overdue_type = []
    overdue_types = db_session.query(IntendedOverdueType).all()
    for type in overdue_types:
        overdue_type.append({"id":type.id,
                               "name": type.name})
    return overdue_type


def get_intended_overdue_result(db_session):
    overdue_result = []
    overdue_results = db_session.query(OverdueResult).all()
    for type in overdue_results:
        overdue_result.append({"id":type.id,
                               "name": type.name})
    return overdue_result
    
    
    
    
def get_juridical_case_details(id, db_session):
    logger.info(f"data: juridical_case_id: {id}")
    juridical_case = {}
    get_juridical_case = db_session.query(JuridicalCase).filter(JuridicalCase.id == id).first()
    
    if get_juridical_case is not None:
        juridical_case ={"id":get_juridical_case.id,
                      "loan_portfolio":{"id":get_juridical_case.portfolio.id,
                                        "bank_mfo":{ "id":get_juridical_case.portfolio.bank_mfo_id,
                                                        "bank_mfo":get_juridical_case.portfolio.loan_branch.code,
                                                        "name":get_juridical_case.portfolio.loan_branch.name}},
                            "main_responsible":{"id":get_juridical_case.main_responsible_id and get_juridical_case.main_responsible.id,
                                          "full_name":get_juridical_case.main_responsible_id and get_juridical_case.main_responsible.full_name,
                                          "bank_mfo":{"id":get_juridical_case.main_responsible_id and get_juridical_case.main_responsible.branch.id,
                                                        "bank_mfo":get_juridical_case.main_responsible_id and get_juridical_case.main_responsible.branch.code,
                                                        "name":get_juridical_case.main_responsible_id and get_juridical_case.main_responsible.branch.name}},
                            "second_responsible":{"id":get_juridical_case.second_responsible and get_juridical_case.second_responsible.id,
                                          "full_name":get_juridical_case.second_responsible and get_juridical_case.second_responsible.full_name,
                                          "bank_mfo":{"id":get_juridical_case.second_responsible and get_juridical_case.second_responsible.branch.id,
                                                        "bank_mfo":get_juridical_case.second_responsible and get_juridical_case.second_responsible.branch.code,
                                                        "name":get_juridical_case.second_responsible and get_juridical_case.second_responsible.branch.name}},
                            "from_user":{"id":get_juridical_case.from_user_id and get_juridical_case.from_user.id,
                                          "full_name":get_juridical_case.from_user_id and get_juridical_case.from_user.full_name,
                                          "bank_mfo":{"id":get_juridical_case.from_user_id and get_juridical_case.from_user.branch.id,
                                                        "bank_mfo":get_juridical_case.from_user_id and get_juridical_case.from_user.branch.code,
                                                        "name":get_juridical_case.from_user_id and get_juridical_case.from_user.branch.name}},
                            "juridical_punishment":get_juridical_case.juridical_punishment_id and get_juridical_case.juridical_punishment_id or None,
                            "intended_overdue_type":get_juridical_case.intended_overdue_type_id and get_juridical_case.type or None,
                            "intended_overdue_result": get_intended_overdue_result(db_session),
                            "juridical_case_status":get_juridical_case.juridical_case_status_id and get_juridical_case.status.name or None,
                            "created_at":get_juridical_case.created_at and get_juridical_case.created_at or None,
                            "updated_at":get_juridical_case.updated_at and get_juridical_case.updated_at or None}
        tasks = TaskManager_class.get_task_manager_by_id(get_juridical_case.task, db_session)
        general_tasks_list = general_tasks_crud.get_general_tasks_by_category_id(get_juridical_case.task.general_task.category.id, db_session)
        params = {"bank_mfo":get_juridical_case.portfolio.bank_mfo_id,
                  "department":get_juridical_case.main_responsible_id and get_juridical_case.main_responsible.department}
        users_by_branch = users.get_all(db_session, params)
        
        return {"juridical_case":juridical_case,
                "task":tasks and tasks or None,
                "general_tasks":general_tasks_list and general_tasks_list or None,
                "users_by_bank_mfo":users_by_branch and users_by_branch or None}
        
        
        
        
        
        
        
        
        
        
def juridical_file_delete_last_files(juridical_case_id,general_task_id, db_session):
    
    get_juridical_history = db_session.query(JuridicalCaseHistory)\
        .filter(JuridicalCaseHistory.juridical_case_id == juridical_case_id)\
            .filter(JuridicalCaseHistory.general_task_id == general_task_id).order_by(JuridicalCaseHistory.id.desc()).first()
    
    for history_file in get_juridical_history.files:
        get_juridical = db_session.query(JuridicalCase).filter(JuridicalCase.id == juridical_case_id).first()
        for case_file in get_juridical.files:
            if case_file.id == history_file.id:
                temp_file = history_file
        get_juridical.files.remove(temp_file)
        db_session.add(get_juridical)
    
    return "OK"
