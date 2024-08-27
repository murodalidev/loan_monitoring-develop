import datetime
from app.models.problems_case.problems_assets.problems_assets_notification_model import ProblemsStateNotification
from app.models.problems_case.judicial_process.judicial_data_history_model import JudicialDataHistory
from app.models.problems_case.problems_case_model import ProblemsCase

from .....models.problems_case.judicial_process.judicial_process_data_model import JudicialData
from .....models.problems_case.judicial_process.judicial_authority import JudicialAuthority
from .....common.is_empty import is_empty, is_exists
from .....common.commit import commit_object, flush_object
from .....common import save_file
from .....common.dictionaries.monitoring_case_dictionary import  problems_assets_status
from .....common.dictionaries.notification_dictionary import notification_type, notification_body
from .....common.dictionaries.case_history_dictionaries import juridical_case_history
from .....common.dictionaries.task_status_dictionaries import task_status
from ...notification.notification_crud import Notificaton_class
from .....schemas.notification_schemas import CreateNotification
from .....config.logs_config import info_logger
import os
from ...problems_case import non_targeted_case
from .....common.dictionaries.general_tasks_dictionary import JGT, MGT, MAIN_DUE_DATE, CASE_HISTORY, DEADLINE_EXT
from app.services.loan_monitoring.problems_case.state_chains import set_chain_state_for_judicial_proccess












def upload_judicial_results(request, file_path, db_session):
    judicial_data = db_session.query(JudicialData).filter(JudicialData.problems_case_id == request.problems_case_id)\
        .filter(JudicialData.type_id == request.judicial_type_id).first()
    if judicial_data is None:
    
    
        
        judicial_data = JudicialData(problems_case_id = request.problems_case_id and request.problems_case_id or None,
                                    type_id = request.judicial_type_id and request.judicial_type_id or None,
                                    region_id = request.region_id and request.region_id or None,
                                    authority_id = request.judicial_authority_id and request.judicial_authority_id or None,
                                    
                                    receipt_date  = request.receipt_date and request.receipt_date or None, 
                                    decision_date_on_admission = request.decision_date_on_admission and request.decision_date_on_admission or None, 
                                    decision_date_to_set = request.decision_date_to_set and request.decision_date_to_set or None, 
                                    decision_date_in_favor_of_bank = request.decision_date_in_favor_of_bank and request.decision_date_in_favor_of_bank or None, 
                                    date_to_set = request.date_to_set and request.date_to_set or None, 
                                    
                                    register_num = request.register_num and request.register_num or None, 
                                    decision_on_admission_num = request.decision_on_admission_num and request.decision_on_admission_num or None, 
                                    decision_to_set_num = request.decision_to_set_num and request.decision_to_set_num or None, 
                                    decision_in_favor_of_bank_num = request.decision_in_favor_of_bank_num and request.decision_in_favor_of_bank_num or None,
                                    
                                    claim_amount = request.claim_amount and request.claim_amount or None,
                                    judicial_status_id = problems_assets_status['на проверку'],
                                    created_at = datetime.datetime.now()
                                    )
    
        db_session.add(judicial_data)
    
    
        info_logger.info("user %s required 'upload_judicial_results' method", request.from_user)
        info_logger.info("user %s sent files: %s", request.from_user, file_path)
    else:
        info_logger.info("user %s repeatedly requested upload_judicial_results method", request.from_user)
        info_logger.info("user %s sent files: %s", request.from_user, file_path)   
        
        
        judicial_data.type_id = request.judicial_type_id and request.judicial_type_id or None,
        judicial_data.region_id = request.region_id and request.region_id or None,
        judicial_data.authority_id = request.judicial_authority_id and request.judicial_authority_id or None,
        
        judicial_data.receipt_date  = request.receipt_date and request.receipt_date or None, 
        judicial_data.decision_date_on_admission = request.decision_date_on_admission and request.decision_date_on_admission or None, 
        judicial_data.decision_date_to_set = request.decision_date_to_set and request.decision_date_to_set or None, 
        judicial_data.decision_date_in_favor_of_bank = request.decision_date_in_favor_of_bank and request.decision_date_in_favor_of_bank or None, 
        judicial_data.date_to_set = request.date_to_set and request.date_to_set or None, 
        
        judicial_data.register_num = request.register_num and request.register_num or None, 
        judicial_data.decision_on_admission_num = request.decision_on_admission_num and request.decision_on_admission_num or None, 
        judicial_data.decision_to_set_num = request.decision_to_set_num and request.decision_to_set_num or None, 
        judicial_data.decision_in_favor_of_bank_num = request.decision_in_favor_of_bank_num and request.decision_in_favor_of_bank_num or None,
        
        judicial_data.claim_amount = request.claim_amount and request.claim_amount or None,
        judicial_data.judicial_status_id = problems_assets_status['на проверку'],
        
        
        
        judicial_data.updated_at = datetime.datetime.now()
    get_problems_case = db_session.query(ProblemsCase).filter(ProblemsCase.id == request.problems_case_id).first()
    get_problems_case.updated_at = datetime.datetime.now()
    get_problems_case.checked_status=False
    
    get_problems_state_notification = db_session.query(ProblemsStateNotification).filter(ProblemsStateNotification.loan_portfolio_id == get_problems_case.loan_portfolio_id).first()
    if get_problems_state_notification is None:
        new_problems_state_notification = ProblemsStateNotification(loan_portfolio_id = get_problems_case.loan_portfolio_id, judicial_status_id = problems_assets_status['на проверку'])
        db_session.add(new_problems_state_notification)
        flush_object(db_session)
    else:
        get_problems_state_notification.judicial_status_id = problems_assets_status['на проверку']
    
    
    data = CreateNotification()
    data.from_user_id = request.from_user
    data.to_user_id = request.to_user
    data.notification_type = notification_type['problems']
    data.body = notification_body['send_to_check_judicial']
    data.url = f'{get_problems_case.loan_portfolio_id}' + ':' + f'{get_problems_case.id}'+ ':' +f'{MGT.JUDICIAL.value}'
    notifiaction = Notificaton_class(data)
    notifiaction.create_notification(db_session)
    
    new_scheduled_history = JudicialDataHistory(problems_case_id = request.problems_case_id, 
                                            type_id = CASE_HISTORY.JUDICIAL.value,
                                            from_user_id = request.from_user, 
                                            to_user_id= request.to_user,
                                            comment = request.comment,
                                            created_at = datetime.datetime.now(),
                                            message = juridical_case_history['send_results_to_check']
                                                )
    db_session.add(new_scheduled_history)
    
    save_file.append_monitoring_files(judicial_data, file_path, db_session)
    
    set_chain_state_for_judicial_proccess(get_problems_case.portfolio.loan_id, db_session)
    
    commit_object(db_session)
    
    return "OK"