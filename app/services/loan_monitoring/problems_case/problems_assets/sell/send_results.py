import datetime

from app.models.problems_case.problems_assets.problems_assets_history_model import ProblemsAssetsHistory
from app.models.problems_case.problems_assets.problems_assets_model import ProblemsAssets
from app.models.problems_case.problems_assets.problems_assets_notification_model import ProblemsStateNotification
from app.models.problems_case.problems_case_model import ProblemsCase
from app.services.loan_monitoring.problems_case.state_chains import set_chain_state_for_out_of_balance, set_chain_state_for_problems_assets

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


def upload_problems_assets_sell_files(request, file_path, db_session):
    problems_assets_data = db_session.query(ProblemsAssets).filter(ProblemsAssets.problems_case_id == request.problems_case_id)\
        .filter(ProblemsAssets.type_id == request.asset_type_id).first()
    
    if problems_assets_data is None:
        
        problems_assets_data = ProblemsAssets(problems_case_id = request.problems_case_id,
                                    type_id = request.asset_type_id and request.asset_type_id or None,
                                    main_responsible_id = request.to_user,
                                    second_responsible_id = request.from_user,
                                    assets_status_id = problems_assets_status['на проверку'],
                                    created_at = datetime.datetime.now()
                                    )
    
        db_session.add(problems_assets_data)
        flush_object(db_session)
        
        problems_assets_data.turn = request.to_user
        info_logger.info("user %s required 'upload_problems_assets_files' method", request.from_user)
        info_logger.info("user %s sent files: %s", request.from_user, file_path)
    else:
        info_logger.info("user %s repeatedly requested upload_problems_assets_files method", request.from_user)
        info_logger.info("user %s sent files: %s", request.from_user, file_path)   
        
        
        problems_assets_data.assets_status_id = problems_assets_status['на проверку'],
        problems_assets_data.turn = request.to_user
        problems_assets_data.updated_at = datetime.datetime.now()
        
    get_problems_case = db_session.query(ProblemsCase).filter(ProblemsCase.id == request.problems_case_id).first()
    get_problems_case.updated_at = datetime.datetime.now()
    get_problems_case.checked_status=False
    
    
    get_problems_state_notification = db_session.query(ProblemsStateNotification).filter(ProblemsStateNotification.loan_portfolio_id == get_problems_case.loan_portfolio_id).first()
    if get_problems_state_notification is None:
        new_problems_state_notification = ProblemsStateNotification(loan_portfolio_id = get_problems_case.loan_portfolio_id, problems_assets_sell_status_id = problems_assets_status['на проверку'])
        db_session.add(new_problems_state_notification)
        flush_object(db_session)
    else:
        get_problems_state_notification.problems_assets_sell_status_id = problems_assets_status['на проверку']
    
    
    data = CreateNotification()
    data.from_user_id = request.from_user
    data.to_user_id = request.to_user
    data.notification_type = notification_type['problems']
    data.body = notification_body['send_to_check_problems_assets']
    data.url = f'{get_problems_case.loan_portfolio_id}' + ':' + f'{get_problems_case.id}'+ ':' +f'{MGT.ASSETS_SELL.value}'
    
    notifiaction = Notificaton_class(data)
    notifiaction.create_notification(db_session)
    
    new_problems_assets_history = ProblemsAssetsHistory(problems_case_id = request.problems_case_id, 
                                            type_id = CASE_HISTORY.ASSETS_SELL.value,
                                            from_user_id = request.from_user, 
                                            to_user_id= request.to_user,
                                            comment = request.comment,
                                            created_at = datetime.datetime.now(),
                                            message = problems_assets_history['send_files_to_chcek']
                                                )
    db_session.add(new_problems_assets_history)
    
    save_file.append_monitoring_files(problems_assets_data, file_path, db_session)
    commit_object(db_session)
    
    return "OK"







def upload_problems_assets_sell_decision(request, file_path, db_session):
    problems_assets_data = db_session.query(ProblemsAssets).filter(ProblemsAssets.id == request.problems_assets_id).first()
    get_problems_case = db_session.query(ProblemsCase).filter(ProblemsCase.id == request.problems_case_id).first()
    
   
    problems_assets_data.assets_status_id = problems_assets_status['завершен']
    get_problems_case.updated_at = datetime.datetime.now()
    get_problems_case.checked_status=False
    problems_assets_data.updated_at = datetime.datetime.now()
    
    
    info_logger.info("user %s required 'upload_problems_assets_sell_decision' method", request.from_user)
    info_logger.info("user %s sent files: %s", request.from_user, file_path)
    
    
    new_problems_assets_history = ProblemsAssetsHistory(problems_case_id = request.problems_case_id, 
                                            type_id = CASE_HISTORY.ASSETS_SELL.value,
                                            from_user_id = request.from_user, 
                                            to_user_id= request.to_user,
                                            comment = request.comment,
                                            created_at = datetime.datetime.now(),
                                            message = problems_assets_history['finished']
                                                )
    db_session.add(new_problems_assets_history)
    
    get_problems_state_notification = db_session.query(ProblemsStateNotification).filter(ProblemsStateNotification.loan_portfolio_id == get_problems_case.loan_portfolio_id).first()
    get_problems_state_notification.problems_assets_sell_status_id = problems_assets_status['завершен']
    
    save_file.append_monitoring_files(problems_assets_data, file_path, db_session, addition=True)
    
    
    set_chain_state_for_problems_assets(get_problems_case.portfolio.loan_id, db_session)
    
    commit_object(db_session)
    
    return "OK"