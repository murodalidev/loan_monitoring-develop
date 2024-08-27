import datetime
import requests

from sqlalchemy import or_
from ....models.notification.monitoring_notification_model import MonitoringNotification
from app.models.users.user_tg_bot_auth import UserTgBotAuth
from ...users.users_crud import Users
from app.models.users.users import Users as UserModel
from ....common.commit import commit_object, flush_object
from sqlalchemy.sql import text
from app.config.config import TELEGRAM_BOT_TOKEN
from app.common.dictionaries.departments_dictionary import DEP
from app.common.dictionaries.notification_dictionary import notification_type

class Notificaton_class():
    def __init__(self, data=None):
        self.data = data
        
        
    def create_notification(self, db_session):
            
        new_notification = MonitoringNotification(from_user_id = self.data.from_user_id and self.data.from_user_id,
                                                    to_user_id = self.data.to_user_id and self.data.to_user_id or None,
                                                    notification_type_id = self.data.notification_type,
                                                    body = self.data.body,
                                                    url = self.data.url,
                                                    created_at = datetime.datetime.now())
        db_session.add(new_notification)

        self.send_to_tg_bot(db_session, {
            "body": self.data.body,
            "from_user_id": self.data.from_user_id,
            # "notification_type_id": self.data.notification_type,
            "to_user_id": self.data.to_user_id,
        })
        
        
    
    
    def get_all(page, size,  user, db_session):
        notifications_list = []
        #get_all_notifications = db_session.query(MonitoringNotification).filter(MonitoringNotification.to_user_id == user.id)
        filter_by_department = ''
        if user.department == DEP.PROBLEM.value:
            filter_by_department = F'''
                                    AND (MN.NOTIFICATION_TYPE_ID = {notification_type['problems']} OR 
                                        MN.NOTIFICATION_TYPE_ID = {notification_type['problem_letter']})
                                '''
        elif user.department == DEP.BUSINESS.value:
            filter_by_department = F'''
                                    AND MN.NOTIFICATION_TYPE_ID = {notification_type['business']}
                                '''
        elif user.department == DEP.KAD.value:
            filter_by_department = F'''
                                    AND (MN.NOTIFICATION_TYPE_ID = {notification_type['monitoring']} OR 
                                        MN.NOTIFICATION_TYPE_ID = {notification_type['target_monitoring']} OR 
                                        MN.NOTIFICATION_TYPE_ID = {notification_type['scheduled_monitoring']} OR 
                                        MN.NOTIFICATION_TYPE_ID = {notification_type['unscheduled_monitoring']})
                                '''
                                
            # get_all_notifications = get_all_notifications.filter(
            #                                         or_(MonitoringNotification.notification_type_id == notification_type['problems'],
            #                                             MonitoringNotification.notification_type_id == notification_type['problem_letter']))\
            #         .filter(MonitoringNotification.is_read == False)
        
        
            
            # get_all_notifications = get_all_notifications.filter(MonitoringNotification.notification_type_id == notification_type['business'])\
            #         .filter(MonitoringNotification.is_read == False)
            
        
            
        #     get_all_notifications = get_all_notifications.filter(
        #                 or_(MonitoringNotification.notification_type_id == notification_type['monitoring'],
        #                     MonitoringNotification.notification_type_id == notification_type['target_monitoring'],
        #                     MonitoringNotification.notification_type_id == notification_type['scheduled_monitoring'],
        #                     MonitoringNotification.notification_type_id == notification_type['unscheduled_monitoring']))\
        #             .filter(MonitoringNotification.is_read == False)
        # get_all_notifications = get_all_notifications.order_by(MonitoringNotification.id.desc()).all()
        
        
        
        get_notifications = db_session.execute(text(f'''
                                                    SELECT 
                                                    U.FULL_NAME,
                                                    U.DEPARTMENT,
                                                    MN.ID,
                                                    MN.FROM_USER_ID,
                                                    MN.TO_USER_ID,
                                                    MNT.NAME AS NOTIFICATION_TYPE_NAME,
                                                    MN.CREATED_AT,
                                                    MN.BODY,
                                                    MN.URL,
                                                    MN.IS_READ
                                                    FROM MONITORING_NOTIFICATION MN
                                                    JOIN MONITORING_NOTIFICATION_TYPE MNT ON MNT.ID=MN.NOTIFICATION_TYPE_ID
                                                    JOIN USERS U ON U.ID=MN.FROM_USER_ID
                                                    WHERE MN.TO_USER_ID = {user.id}
                                                    {filter_by_department}
                                                    ORDER BY MN.ID DESC
                                                    LIMIT {size} OFFSET ({page} - 1) * {size}
                                                  ''')).fetchall()
        
        
        
        
        for notification in get_notifications:
            notifications_list.append({ "id": notification.id,
                                        "from_user":notification.full_name,
                                        "notification_type_name": notification.notification_type_name,
                                        "is_read": notification.is_read,
                                        "created_at": notification.created_at,
                                        "body": notification.body,
                                        "url": notification.url
            })
            
            
        return {"items": notifications_list,
            "page":page,
            "size":size} 
        return notifications_list

    def read_notification(self, db_session):
        notification = db_session.query(MonitoringNotification).filter(MonitoringNotification.id == self.data.notification_id).first()
        notification.is_read = True

        commit_object(db_session)
        return {"notification_id":notification.id,
                "is_read":notification.is_read}
    
    def read_all(self, db_session):
        notifications = db_session.query(MonitoringNotification).filter(MonitoringNotification.to_user_id == self.data.user_id).all()
        for notif in notifications:
            notif.is_read = True
            flush_object(db_session)
        commit_object(db_session)

        return "OK"
    
    def read_all_for_user(self, db_session):
        notifications = db_session.query(MonitoringNotification).filter(MonitoringNotification.id.in_(tuple(self.data.notifications))).all()
        
        for notif in notifications:
            notif.is_read = True
            flush_object(db_session)
        commit_object(db_session)

        return "OK"
    
    

    def send_to_tg_bot(self, db_session, task):
        telegram_chat_id = db_session.query(UserTgBotAuth.user_tg_bot_id).filter(UserTgBotAuth.user_id == task["to_user_id"]).first()
        
        #request = requests.get(getUrl(telegram_chat_id, message))
        

def getUrl(telegram_chat_id, message):
    return 'https://api.telegram.org/bot' + TELEGRAM_BOT_TOKEN +  '/sendMessage?chat_id=' + str(telegram_chat_id[0]) + '&parse_mode=HTML&text=' + message