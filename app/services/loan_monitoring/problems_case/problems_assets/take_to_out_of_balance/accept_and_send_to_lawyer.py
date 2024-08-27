import datetime
from app.models.problems_case.out_of_balance.out_of_balance_history_model import OutOfBalanceHistory
from app.models.problems_case.out_of_balance.out_of_balance_model import OutOfBalance
from app.models.problems_case.problems_assets.problems_assets_notification_model import ProblemsStateNotification
from app.models.problems_case.problems_case_model import ProblemsCase
from app.models.problems_case.problems_monitoring_expiration_model import ProblemsMonitoringExpiration
from app.models.problems_case.problems_monitoring_model import ProblemsMonitoring
from app.models.problems_case.judicial_process.judicial_data_history_model import JudicialDataHistory

from ......common.is_empty import is_empty, is_exists
from ......common.commit import commit_object, flush_object
from ......common import save_file
from dateutil.relativedelta import relativedelta
from ......schemas.juridical_case_schemas import SendToProblemAfterTarget
from ....juridical_case import juridical_case_crud
from .....monitoring_files import files_crud
from ....task_manager.task_manager_crud import TaskManager_class
from ......common.dictionaries.monitoring_case_dictionary import  problems_assets_status
from ......common.dictionaries.notification_dictionary import notification_type, notification_body
from ......common.dictionaries.case_history_dictionaries import loan_case_history, problems_assets_history
from ....notification.notification_crud import Notificaton_class
from ......schemas.notification_schemas import CreateNotification
from ......config.logs_config import info_logger
import os
from ....problems_case import non_targeted_case
from ......common.dictionaries.general_tasks_dictionary import JGT, MGT, MAIN_DUE_DATE, CASE_HISTORY, DEADLINE_EXT
from ....monitoring_case.script_date_holidays import get_business_days
from ......common.dictionaries.departments_dictionary import  ROLES, DEP
from ......models.users.users import Users as user, user_role
from ......common.is_empty import is_exists

def accept_or_rework_out_of_balance_data(request, db_session):
    info_logger.info("user %s required 'accept_or_rework_out_of_balance_data' method", request.from_user)
    out_of_balance_data = db_session.query(OutOfBalance).filter(OutOfBalance.id == request.out_of_balance_id).first()
    get_problems_case = db_session.query(ProblemsCase).filter(ProblemsCase.id == request.problems_case_id).first()
    get_problems_state_notification = db_session.query(ProblemsStateNotification).filter(ProblemsStateNotification.loan_portfolio_id == get_problems_case.loan_portfolio_id).first()
    
    get_problems_case.updated_at = datetime.datetime.now()
    get_problems_case.checked_status=False
    if request.result_type:
        
        get_lawyer = db_session.query(user.id).filter(user.department == DEP.PROBLEM.value).join(user_role)\
            .filter(user_role.columns.role_id == ROLES.problem_block_lawyer.value).first()
        is_exists(get_lawyer, 400, 'Lawyer not found')
        
        status = problems_assets_status['юристу']
        message = problems_assets_history['accepted_and_send']
        body = notification_body['accept_out_of_balance']
        
        
        out_of_balance_data.third_responsible_id = get_lawyer.id
        out_of_balance_data.turn = get_lawyer.id
        get_problems_state_notification.out_of_balance_status_id = problems_assets_status['юристу']
        
        new_out_of_balance_history = OutOfBalanceHistory(problems_case_id = request.problems_case_id, 
                                            from_user_id = request.from_user, 
                                            to_user_id= get_lawyer.id,
                                            comment = request.comment,
                                            created_at = datetime.datetime.now(),
                                            message = message
                                                )
        db_session.add(new_out_of_balance_history)
        
        
        data = CreateNotification()
        data.from_user_id = request.from_user 
        data.to_user_id =get_lawyer.id
        data.notification_type = notification_type['problems']
        data.body = body
        data.url = f'{get_problems_case.loan_portfolio_id}' + ':' + f'{get_problems_case.id}'+ ':' +f'{MGT.OUT_OF_BALANCE.value}'
        notifiaction = Notificaton_class(data)
        notifiaction.create_notification(db_session)
        
        
    else:
        status = problems_assets_status['переделать']
        message = problems_assets_history['rework']
        body = notification_body['rework_out_of_balance']
        
        out_of_balance_data.turn = request.to_user
        get_problems_state_notification.out_of_balance_status_id = problems_assets_status['переделать']
        
        file_path = files_crud.set_wrong_files(request.wrong_files, out_of_balance_data, db_session)
        flush_object(db_session)
        info_logger.info("user %s sent out_of_balance to rework", request.from_user)
        info_logger.info("user %s sent to rework files: %s", request.from_user, file_path)
        new_out_of_balance_history = OutOfBalanceHistory(problems_case_id = request.problems_case_id,
                                            from_user_id = request.from_user, 
                                            to_user_id= request.to_user,
                                            comment = request.comment,
                                            created_at = datetime.datetime.now(),
                                            message = message
                                                )
        db_session.add(new_out_of_balance_history)
        
        
        data = CreateNotification()
        data.from_user_id = request.from_user 
        data.to_user_id =request.to_user
        data.notification_type = notification_type['problems']
        data.body = body
        data.url = f'{get_problems_case.loan_portfolio_id}' + ':' + f'{get_problems_case.id}'+ ':' +f'{MGT.OUT_OF_BALANCE.value}'
        notifiaction = Notificaton_class(data)
        notifiaction.create_notification(db_session)
        
    out_of_balance_data.out_of_balance_status_id = status
    
    commit_object(db_session)
    
    return "OK"