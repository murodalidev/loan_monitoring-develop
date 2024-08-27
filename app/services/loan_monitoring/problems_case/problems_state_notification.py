from app.models.problems_case.problems_assets.problems_assets_notification_model import ProblemsStateNotification
from ....common.dictionaries.monitoring_case_dictionary import  monitoring_status, problems_assets_status



def get_promblems_state_notifications(loan_portfolio_id, user_id, main_responsible_id, second_responsible_id, db_session):
    
    problems_assets_get = False
    problems_assets_get_notif = False
    problems_assets_sell = False
    problems_assets_sell_notif = False
    judicial = False
    judicial_notif = False
    out_of_balance = False
    out_of_balance_notif = False
    letter_35 = False
    letter_45 = False
    bpi_ended = False
    bpi_ended_notif = False
    auction = False
    auction_notif = False
    
    get_problems_state_notitification = db_session.query(ProblemsStateNotification).filter(ProblemsStateNotification.loan_portfolio_id == loan_portfolio_id).first()
    if get_problems_state_notitification is not None:
        if (get_problems_state_notitification.judicial_status_id == problems_assets_status['на проверку'] and user_id == main_responsible_id) or\
            (get_problems_state_notitification.judicial_status_id == problems_assets_status['переделать'] and user_id == second_responsible_id) or\
                (get_problems_state_notitification.judicial_status_id == problems_assets_status['проверено']):
            judicial = True
            judicial_notif = True
        
            if get_problems_state_notitification.judicial_status_id == problems_assets_status['проверено']:
                judicial_notif = False
        
        if ((get_problems_state_notitification.problems_assets_get_status_id == problems_assets_status['на проверку'] or\
            get_problems_state_notitification.problems_assets_get_status_id == problems_assets_status['юрист отправил']) and user_id == main_responsible_id) or\
            (get_problems_state_notitification.problems_assets_get_status_id == problems_assets_status['переделать'] and user_id == second_responsible_id) or\
                (get_problems_state_notitification.problems_assets_get_status_id == problems_assets_status['завершен']):
            problems_assets_get = True
            problems_assets_get_notif = True
            
            if get_problems_state_notitification.problems_assets_get_status_id == problems_assets_status['завершен']:
                problems_assets_get_notif = False
        
        if ((get_problems_state_notitification.problems_assets_sell_status_id == problems_assets_status['на проверку'] or\
            get_problems_state_notitification.problems_assets_sell_status_id == problems_assets_status['юрист отправил']) and user_id == main_responsible_id) or\
            (get_problems_state_notitification.problems_assets_sell_status_id == problems_assets_status['переделать'] and user_id == second_responsible_id) or\
                (get_problems_state_notitification.problems_assets_sell_status_id == problems_assets_status['завершен']):
            problems_assets_sell = True
            problems_assets_sell_notif = True
            
            if get_problems_state_notitification.problems_assets_sell_status_id == problems_assets_status['завершен']:
                problems_assets_sell_notif = False
                
                
        if ((get_problems_state_notitification.out_of_balance_status_id == problems_assets_status['на проверку'] or\
             get_problems_state_notitification.out_of_balance_status_id == problems_assets_status['юрист отправил']) and user_id == main_responsible_id) or\
            (get_problems_state_notitification.out_of_balance_status_id == problems_assets_status['переделать'] and user_id == second_responsible_id) or\
                (get_problems_state_notitification.out_of_balance_status_id == problems_assets_status['завершен']):
            out_of_balance = True
            out_of_balance_notif = True
            
            if get_problems_state_notitification.out_of_balance_status_id == problems_assets_status['завершен']:
                out_of_balance_notif = False
        
        if ((get_problems_state_notitification.bpi_ended_status == problems_assets_status['на проверку']) and user_id == main_responsible_id) or\
            (get_problems_state_notitification.bpi_ended_status == problems_assets_status['переделать'] and user_id == second_responsible_id) or\
                (get_problems_state_notitification.bpi_ended_status == problems_assets_status['проверено']):
            bpi_ended = True
            bpi_ended_notif = True
            
            if get_problems_state_notitification.bpi_ended_status == problems_assets_status['проверено']:
                bpi_ended_notif = False
        
        if ((get_problems_state_notitification.auction_status == problems_assets_status['на проверку']) and user_id == main_responsible_id) or\
            (get_problems_state_notitification.auction_status == problems_assets_status['переделать'] and user_id == second_responsible_id) or\
                (get_problems_state_notitification.auction_status == problems_assets_status['проверено']):
            auction = True
            auction_notif = True
            
            if get_problems_state_notitification.auction_status == problems_assets_status['проверено']:
                auction_notif = False
        
        
        
        letter_35 = get_problems_state_notitification.letter_35_status_id and get_problems_state_notitification.letter_35_status_id or False
        letter_45 = get_problems_state_notitification.letter_45_status_id and get_problems_state_notitification.letter_45_status_id or False
        
        
        
    return {"judicial":{'status':judicial,
                        'notification': judicial_notif},
            "problems_assets_get":{'status':problems_assets_get,
            'notification':problems_assets_get_notif},
            "problems_assets_sell":{'status':problems_assets_sell,
            'notification':problems_assets_sell_notif},
            "out_of_balance":{'status':out_of_balance,
            'notification':out_of_balance_notif},
            "letter_35":{'status':letter_35,
            'notification':False},
            "letter_45":{'status':letter_45,
            'notification':False},
            "bpi_ended_status":{'status':bpi_ended,
            'notification':bpi_ended_notif},
            "auction_status":{'status':auction,
            'notification':auction_notif}}
    