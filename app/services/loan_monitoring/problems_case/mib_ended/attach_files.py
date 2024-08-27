import datetime
import os
from app.models.problems_case.judicial_process.judicial_data_history_model import JudicialDataHistory
from app.models.problems_case.mib_ended.mib_ended_history_model import MibEndedHistory
from app.models.problems_case.mib_ended.mib_model import ProblemsMib
from app.models.problems_case.mib_ended.mib_type_model import ProblemsMibType
from app.models.problems_case.mib_ended.mib_files_model import ProblemsMibFiles
from app.models.problems_case.problems_assets.problems_assets_notification_model import ProblemsStateNotification
from app.models.problems_case.problems_case_model import ProblemsCase
from .....common.commit import commit_object, flush_object
from ...notification.notification_crud import Notificaton_class
from .....schemas.notification_schemas import CreateNotification
from .....common.dictionaries.monitoring_case_dictionary import  problems_assets_status
from .....common.dictionaries.notification_dictionary import notification_type, notification_body
from .....common.dictionaries.case_history_dictionaries import problems_assets_history
from app.services.loan_monitoring.problems_case.state_chains import set_chain_state_for_bpi_ended
from .....config.logs_config import info_logger
from .....common.dictionaries.general_tasks_dictionary import CASE_HISTORY, MGT

def upload_mib_files(request, file_path, db_session):
    mib_data = db_session.query(ProblemsMib).filter(ProblemsMib.problems_case_id == request.problems_case_id)\
        .filter(ProblemsMib.type_id == request.mib_type_id).first()
    get_problems_case = db_session.query(ProblemsCase).filter(ProblemsCase.id == request.problems_case_id).first()
    get_problems_case.updated_at = datetime.datetime.now()
    get_problems_case.checked_status=False
    if mib_data is None:
        
        mib_data = ProblemsMib(problems_case_id = request.problems_case_id,
                                    type_id = request.mib_type_id and request.mib_type_id or None,
                                    mib_ended_status_id = problems_assets_status['на проверку'],
                                    created_at = datetime.datetime.now()
                                    )
    
        db_session.add(mib_data)
        flush_object(db_session)
        info_logger.info("user %s required 'upload_mib_files' method", request.from_user)
        info_logger.info("user %s sent files: %s", request.from_user, file_path)
    
    else:
        info_logger.info("user %s repeatedly requested upload_mib_files method", request.from_user)
        info_logger.info("user %s sent files: %s", request.from_user, file_path)   
        
        
        mib_data.mib_ended_status_id = problems_assets_status['на проверку']
        
        mib_data.updated_at = datetime.datetime.now()
    message = problems_assets_history['send_files_to_chcek']
    new_mib_ended_data_history = MibEndedHistory(problems_case_id = request.problems_case_id, 
                                            type_id = CASE_HISTORY.AUCTION.value,
                                            from_user_id = request.from_user, 
                                            to_user_id= request.to_user,
                                            comment = request.comment,
                                            created_at = datetime.datetime.now(),
                                            message = message
                                                )
    db_session.add(new_mib_ended_data_history)    
    
    
    data = CreateNotification()
    data.from_user_id = request.from_user
    data.to_user_id = get_problems_case.main_responsible_id
    data.notification_type = notification_type['problems']
    data.body = notification_body['send_to_check_mib']
    data.url = f'{get_problems_case.loan_portfolio_id}' + ':' + f'{get_problems_case.id}'+ ':' +f'{MGT.MIB_ENDED.value}'
    notifiaction = Notificaton_class(data)
    notifiaction.create_notification(db_session)
    
    
    get_problems_state_notification = db_session.query(ProblemsStateNotification).filter(ProblemsStateNotification.loan_portfolio_id == get_problems_case.loan_portfolio_id).first()
    if get_problems_state_notification is None:
        new_problems_state_notification = ProblemsStateNotification(loan_portfolio_id = get_problems_case.loan_portfolio_id, bpi_ended_status = problems_assets_status['на проверку'])
        db_session.add(new_problems_state_notification)
        flush_object(db_session)
    else:
        get_problems_state_notification.bpi_ended_status = problems_assets_status['на проверку']
    
    append_mib_ended_files(mib_data, file_path, db_session)
    commit_object(db_session)
    
    return "OK"




def get_mib(problems_case_id, db_session):
    
    mib = db_session.query(ProblemsMib).filter(ProblemsMib.problems_case_id == problems_case_id).first()
    states = []
    if mib is not None:
        
            
        states = {"id": mib.id,
                    "problems_case_id": mib.problems_case_id,
                    "mib_ended_status_id":mib.mib_ended_status_id,
                    "type":mib.type_id and mib.type or None,
                    "created_at": mib.created_at,
                    "updated_at": mib.updated_at,
                    "files": mib.files}
            
    return states  






def get_mib_types(db_session):
    
    mib_types = db_session.query(ProblemsMibType).order_by(ProblemsMibType.id.asc()).all()
    types = []
    
    for mib_type in mib_types:
        types.append({"id": mib_type.id,
                    "name": mib_type.name,
                    "code":mib_type.code,
                    })
        
    return types













def  append_mib_ended_files(monitoring, file_path, db_session, addition=None):
    f_list = []
    is_changed = False
    is_files_exist = False
    if monitoring.files != []:
        f_list = [{"id":file.id,"url": file.file_url, "is_correct": file.is_correct} for file in monitoring.files]
        is_files_exist = True
    for fil in f_list:
        
        if fil['is_correct'] == False:
            is_changed = True
            os.remove(fil['url'])
            get_file = db_session.query(ProblemsMibFiles).filter(ProblemsMibFiles.id==fil["id"]).first()
            monitoring.files.remove(get_file)
            db_session.add(monitoring)
            db_session.delete(get_file)
            commit_object(db_session)
    if is_files_exist and  not is_changed and addition is None:
        return 0
    else:
        for file in file_path:
            new_file = ProblemsMibFiles(file_url = file['name'],
                                        is_changed = is_changed,
                                        created_at = datetime.datetime.now())
            db_session.add(new_file)
            flush_object(db_session)
            monitoring.files.append(new_file)
            db_session.add(monitoring)