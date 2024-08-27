import datetime

from app.models.problems_case.out_of_balance.out_of_balance_history_model import OutOfBalanceHistory
from app.models.problems_case.out_of_balance.out_of_balance_model import OutOfBalance
from app.models.problems_case.problems_assets.problems_assets_notification_model import ProblemsStateNotification
from app.models.problems_case.problems_case_model import ProblemsCase
from app.services.loan_monitoring.problems_case.state_chains import set_chain_state_for_out_of_balance

from ......models.problems_case.judicial_process.judicial_process_data_model import JudicialData
from ......models.problems_case.judicial_process.judicial_authority import JudicialAuthority
from ......common.is_empty import is_empty, is_exists
from ......common.commit import commit_object, flush_object
from ......common import save_file
from ......common.dictionaries.monitoring_case_dictionary import  problems_assets_status
from ......common.dictionaries.notification_dictionary import notification_type, notification_body
from ......common.dictionaries.case_history_dictionaries import problems_assets_history
from ......common.dictionaries.task_status_dictionaries import task_status
from ....notification.notification_crud import Notificaton_class
from ......schemas.notification_schemas import CreateNotification
from ......config.logs_config import info_logger
import os
from ....problems_case import non_targeted_case
from ......common.dictionaries.general_tasks_dictionary import JGT, MGT, MAIN_DUE_DATE, CASE_HISTORY, DEADLINE_EXT


def upload_out_of_balance_files(request, file_path, db_session):
    out_of_balance_data = db_session.query(OutOfBalance).filter(OutOfBalance.problems_case_id == request.problems_case_id).first()
    
    if out_of_balance_data is None:
        
        out_of_balance_data = OutOfBalance(problems_case_id = request.problems_case_id,
                                    main_responsible_id = request.to_user,
                                    second_responsible_id = request.from_user,
                                    out_of_balance_status_id = problems_assets_status['на проверку'],
                                    created_at = datetime.datetime.now()
                                    )
    
        db_session.add(out_of_balance_data)
        flush_object(db_session)
        
        out_of_balance_data.turn = request.to_user
        info_logger.info("user %s required 'upload_out_of_balance_files' method", request.from_user)
        info_logger.info("user %s sent files: %s", request.from_user, file_path)
    else:
        info_logger.info("user %s repeatedly requested upload_out_of_balance_files method", request.from_user)
        info_logger.info("user %s sent files: %s", request.from_user, file_path)   
        
        
        out_of_balance_data.out_of_balance_status_id = problems_assets_status['на проверку'],
        out_of_balance_data.turn = request.to_user
        
        out_of_balance_data.updated_at = datetime.datetime.now()
        
    get_problems_case = db_session.query(ProblemsCase).filter(ProblemsCase.id == request.problems_case_id).first()
    get_problems_case.updated_at = datetime.datetime.now()
    get_problems_case.checked_status=False
    get_problems_case.checked_status=False
    
    get_problems_state_notification = db_session.query(ProblemsStateNotification).filter(ProblemsStateNotification.loan_portfolio_id == get_problems_case.loan_portfolio_id).first()
    if get_problems_state_notification is None:
        new_problems_state_notification = ProblemsStateNotification(loan_portfolio_id = get_problems_case.loan_portfolio_id, out_of_balance_status_id = problems_assets_status['на проверку'])
        db_session.add(new_problems_state_notification)
        flush_object(db_session)
    else:
        get_problems_state_notification.out_of_balance_status_id = problems_assets_status['на проверку']
    
    
    data = CreateNotification()
    data.from_user_id = request.from_user
    data.to_user_id = request.to_user
    data.notification_type = notification_type['problems']
    data.body = notification_body['send_to_check_out_of_balance']
    data.url = f'{get_problems_case.loan_portfolio_id}' + ':' + f'{get_problems_case.id}'+ ':' +f'{MGT.OUT_OF_BALANCE.value}'
    
    notifiaction = Notificaton_class(data)
    notifiaction.create_notification(db_session)
    
    new_out_of_balance_history = OutOfBalanceHistory(problems_case_id = request.problems_case_id, 
                                            from_user_id = request.from_user, 
                                            to_user_id= request.to_user,
                                            comment = request.comment,
                                            created_at = datetime.datetime.now(),
                                            message = problems_assets_history['send_files_to_chcek']
                                                )
    db_session.add(new_out_of_balance_history)
    
    save_file.append_monitoring_files(out_of_balance_data, file_path, db_session)
    commit_object(db_session)
    
    return "OK"












def upload_out_of_balance_decision(request, file_path, db_session):
    out_of_balance_data = db_session.query(OutOfBalance).filter(OutOfBalance.id == request.out_of_balance_id).first()
    get_problems_case = db_session.query(ProblemsCase).filter(ProblemsCase.id == request.problems_case_id).first()
    
   
    out_of_balance_data.out_of_balance_status_id = problems_assets_status['завершен']
    get_problems_case.updated_at = datetime.datetime.now()
    get_problems_case.checked_status=False
    
    
    info_logger.info("user %s required 'upload_out_of_balance_decision' method", request.from_user)
    info_logger.info("user %s sent files: %s", request.from_user, file_path)
    
    
    new_out_of_balance_history = OutOfBalanceHistory(problems_case_id = request.problems_case_id, 
                                            from_user_id = request.from_user, 
                                            to_user_id= request.to_user,
                                            comment = request.comment,
                                            created_at = datetime.datetime.now(),
                                            message = problems_assets_history['finished']
                                                )
    db_session.add(new_out_of_balance_history)
    
    save_file.append_monitoring_files(out_of_balance_data, file_path, db_session, addition=True)
    
    get_problems_state_notification = db_session.query(ProblemsStateNotification).filter(ProblemsStateNotification.loan_portfolio_id == get_problems_case.loan_portfolio_id).first()
    get_problems_state_notification.out_of_balance_status_id = problems_assets_status['завершен']
    
    
    set_chain_state_for_out_of_balance(get_problems_case.portfolio.loan_id, db_session)
    
    commit_object(db_session)
    
    return "OK"