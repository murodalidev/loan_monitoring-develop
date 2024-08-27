import datetime
import os
from app.models.problems_case.auction.auction_files_model import ProblemsAuctionFiles
from app.models.problems_case.auction.auction_model import ProblemsAuction
from app.models.problems_case.auction.auction_type_model import ProblemsAuctionType
from app.models.problems_case.mib_ended.mib_ended_history_model import MibEndedHistory
from app.models.problems_case.problems_assets.problems_assets_notification_model import ProblemsStateNotification
from app.models.problems_case.problems_case_model import ProblemsCase
from .....common.commit import commit_object, flush_object
from ...notification.notification_crud import Notificaton_class
from .....schemas.notification_schemas import CreateNotification
from .....common.dictionaries.monitoring_case_dictionary import  problems_assets_status
from .....common.dictionaries.case_history_dictionaries import problems_assets_history
from .....common.dictionaries.notification_dictionary import notification_type, notification_body
from app.services.loan_monitoring.problems_case.state_chains import set_chain_state_for_auction
from .....config.logs_config import info_logger
from .....common.dictionaries.general_tasks_dictionary import CASE_HISTORY, MGT

def upload_auction_files(request, file_path, db_session):
    auction_data = db_session.query(ProblemsAuction).filter(ProblemsAuction.problems_case_id == request.problems_case_id)\
        .filter(ProblemsAuction.type_id == request.auction_type_id).first()
    get_problems_case = db_session.query(ProblemsCase).filter(ProblemsCase.id == request.problems_case_id).first()
    get_problems_case.updated_at = datetime.datetime.now()
    get_problems_case.checked_status=False
    if auction_data is None:
        
        auction_data = ProblemsAuction(problems_case_id = request.problems_case_id,
                                       auction_status_id = problems_assets_status['на проверку'],
                                    type_id = request.auction_type_id and request.auction_type_id or None,
                                    created_at = datetime.datetime.now()
                                    )
    
        db_session.add(auction_data)
        flush_object(db_session)
        auction_data.problem_case.updated_at = datetime.datetime.now()
        info_logger.info("user %s required 'upload_auction_files' method", request.from_user)
        info_logger.info("user %s sent files: %s", request.from_user, file_path)
    
        for file in file_path:
            new_auction_file = ProblemsAuctionFiles(problems_auction_id = auction_data.id,
                                    file_url = file['name'],
                                    created_at =  datetime.datetime.now())
            db_session.add(new_auction_file)
            commit_object(db_session)
    else:
        info_logger.info("user %s repeatedly requested upload_auction_files method", request.from_user)
        info_logger.info("user %s sent files: %s", request.from_user, file_path)   
        
        
        auction_data.auction_status_id = problems_assets_status['на проверку']
        
        auction_data.updated_at = datetime.datetime.now()
    
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
    data.body = notification_body['send_to_check_judicial']
    data.url = f'{get_problems_case.loan_portfolio_id}' + ':' + f'{get_problems_case.id}'+ ':' +f'{MGT.AUCTION.value}'
    notifiaction = Notificaton_class(data)
    notifiaction.create_notification(db_session)
    
    set_chain_state_for_auction(get_problems_case.portfolio.loan_id, db_session)
    
    
    get_problems_state_notification = db_session.query(ProblemsStateNotification).filter(ProblemsStateNotification.loan_portfolio_id == get_problems_case.loan_portfolio_id).first()
    if get_problems_state_notification is None:
        new_problems_state_notification = ProblemsStateNotification(loan_portfolio_id = get_problems_case.loan_portfolio_id, auction_status = problems_assets_status['на проверку'])
        db_session.add(new_problems_state_notification)
        flush_object(db_session)
    else:
        get_problems_state_notification.auction_status = problems_assets_status['на проверку']
    
    append_auction_files(auction_data, file_path, db_session)
    commit_object(db_session)
    
    return "OK"




def get_auction(problems_case_id, auction_type_id, db_session):
    
    auctions = db_session.query(ProblemsAuction).filter(ProblemsAuction.problems_case_id == problems_case_id)\
        .filter(ProblemsAuction.type_id == auction_type_id).all()
    states = []
    if auctions is not None:
        for auction in  auctions:
            
            states = {"id": auction.id,
                        "problems_case_id": auction.problems_case_id,
                        "auction_status_id":auction.auction_status_id,
                        "type":auction.type_id and auction.type or None,
                        "created_at": auction.created_at,
                        "updated_at": auction.updated_at,
                        "files": auction.files}
            
        return states  






def get_auction_types(db_session):
    
    auction_types = db_session.query(ProblemsAuctionType).order_by(ProblemsAuctionType.id.asc()).all()
    types = []
    
    for auction_type in auction_types:
        types.append({"id": auction_type.id,
                    "name": auction_type.name,
                    "code":auction_type.code,
                    })
        
    return types








def  append_auction_files(monitoring, file_path, db_session, addition=None):
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
            get_file = db_session.query(ProblemsAuctionFiles).filter(ProblemsAuctionFiles.id==fil["id"]).first()
            monitoring.files.remove(get_file)
            db_session.add(monitoring)
            db_session.delete(get_file)
            commit_object(db_session)
    if is_files_exist and  not is_changed and addition is None:
        return 0
    else:
        for file in file_path:
            new_file = ProblemsAuctionFiles(file_url = file['name'],
                                        is_changed = is_changed,
                                        created_at = datetime.datetime.now())
            db_session.add(new_file)
            flush_object(db_session)
            monitoring.files.append(new_file)
            db_session.add(monitoring)