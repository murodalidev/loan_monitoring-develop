import datetime

from app.models.problems_case.out_of_balance.out_of_balance_history_model import OutOfBalanceHistory
from app.models.problems_case.out_of_balance.out_of_balance_model import OutOfBalance
from app.models.problems_case.problems_assets.problems_assets_notification_model import ProblemsStateNotification
from app.models.problems_case.problems_case_model import ProblemsCase

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
from ......common.dictionaries.general_tasks_dictionary import JGT, MGT, CASE_HISTORY, DEADLINE_EXT


def upload_out_of_balance_lawyer_decision_file(request, file_path, db_session):
    out_of_balance_data = db_session.query(OutOfBalance).filter(OutOfBalance.id == request.out_of_balance_id).first()
    
    
    out_of_balance_data.turn = request.to_user
    out_of_balance_data.out_of_balance_status_id = problems_assets_status['юрист отправил'],
    out_of_balance_data.updated_at = datetime.datetime.now()
    
    info_logger.info("user %s required 'upload_out_of_balance_lawyer_decision_file' method", request.from_user)
    info_logger.info("user %s sent files: %s", request.from_user, file_path)
    
    
        
    get_problems_case = db_session.query(ProblemsCase).filter(ProblemsCase.id == request.problems_case_id).first()
    get_problems_case.updated_at = datetime.datetime.now()
    get_problems_case.checked_status=False
    
    get_problems_state_notification = db_session.query(ProblemsStateNotification).filter(ProblemsStateNotification.loan_portfolio_id == get_problems_case.loan_portfolio_id).first()
    get_problems_state_notification.out_of_balance_status_id = problems_assets_status['юрист отправил']
    
    data = CreateNotification()
    data.from_user_id = request.from_user
    data.to_user_id = request.to_user
    data.notification_type = notification_type['problems']
    data.body = notification_body['judicial_sent_file']
    data.url = f'{get_problems_case.loan_portfolio_id}' + ':' + f'{get_problems_case.id}'+ ':' +f'{MGT.OUT_OF_BALANCE.value}'
    
    notifiaction = Notificaton_class(data)
    notifiaction.create_notification(db_session)
    
    new_out_of_balance_history = OutOfBalanceHistory(problems_case_id = request.problems_case_id, 
                                            from_user_id = request.from_user, 
                                            to_user_id= request.to_user,
                                            comment = request.comment,
                                            created_at = datetime.datetime.now(),
                                            message = problems_assets_history['judicial_send_file']
                                                )
    db_session.add(new_out_of_balance_history)
    
    save_file.append_monitoring_files(out_of_balance_data, file_path, db_session, addition=True)
    commit_object(db_session)
    
    return "OK"