import datetime
from sqlalchemy import or_, and_, cast, Date

from app.models.users.user_tg_bot_auth import UserTgBotAuth
from app.models.notification.monitoring_notification_model import MonitoringNotification
from app.models.users.users import Users
from ..users.users_crud import Users as UserClass

from app.models.monitoring_case.target_monitoring_expiration_model import TargetMonitoringExpiration
from app.models.monitoring_case.scheduled_monitoring_expiration_model import ScheduledMonitoringExpiration
from app.models.monitoring_case.unscheduled_monitoring.unscheduled_monitoring_expiration_model import UnscheduledMonitoringExpiration
from app.models.monitoring_case.monitoring_case_model import MonitoringCase
from app.models.monitoring_case.target_monitoring_model import TargetMonitoring
from app.models.monitoring_case.scheduled_monitoring_model import ScheduledMonitoring
from app.models.monitoring_case.unscheduled_monitoring.unscheduled_monitoring_model import UnscheduledMonitoring
from app.models.loan_case.loan_case_model import LoanCase
from app.models.brief_case.loan_portfolio import Loan_Portfolio
from ...common.commit import commit_object
from  app.services.loan_monitoring.monitoring_case.script_date_holidays import get_business_days



def check_exist_user(db_session, tg_user_id, user_id, token):
    user = db_session.query(UserTgBotAuth)
    if tg_user_id is not None:
        user = user.filter(UserTgBotAuth.user_tg_bot_id == tg_user_id)
    if user_id is not None:
        user = user.filter(UserTgBotAuth.user_id == user_id)
    if token is not None:
        user = user.filter(UserTgBotAuth.tg_bot_token == token)
    
    user = user.first()
    if user is not None:
        return {
                "result": True,
                "user": {
                    "user_id": user.user_id,
                    "tg_user_id": user.user_tg_bot_id
                }
            }
    
    return {"result": False,
            "user": {}
            }

def get_user_by_param(db_sesion, user_id, username):
    user = db_sesion.query(Users)
    if user_id is not None:
        user = user.filter(Users.id == user_id)
    if username is not None:
        user = user.filter(Users.username == username)

    user = user.first()
    if user is None:
        return {
            "result": False,
            "user": {}
        }
    
    return { 
                "result": True,
                "user": {
                    "id": user.id,
                    "user_name": user.full_name
                }
            }

def create_user(db_session, tg_user_id, user_id):
    user = db_session.query(UserTgBotAuth).filter(UserTgBotAuth.user_id == user_id).first()
    
    user.user_tg_bot_id = tg_user_id

    commit_object(db_session)


    return {"status": "OK"}


def get_active_notification(db_session, user_id, page):
    today = datetime.datetime.now().date()
    
    
    count = db_session.query(MonitoringNotification).filter(MonitoringNotification.to_user_id == user_id).count()
    notifications = db_session.query(MonitoringNotification).filter(MonitoringNotification.to_user_id == user_id).order_by(MonitoringNotification.id.desc()).limit(10).offset(page * 10).all()

    notifications_list = []

    for notification in notifications:
        notifications_list.append({
                                    "id": notification.id,
                                    "from_user": notification.from_user_id and UserClass.get_user_by_id(notification.from_user_id, db_session)['full_name'] or None,
                                    "notification_type": notification.notification_type_id and notification.type or None,
                                    "created_at": notification.created_at,
                                    "body": notification.body,
        })

    return [notifications_list, count]

def get_deadlines(db_session, user_id, days, page):
    deadlines_list = []

    today = datetime.datetime.today()
    deadline_day = get_business_days(today, days, db_session)
    target_deadlines = db_session.query(TargetMonitoringExpiration, Loan_Portfolio.loan_id)\
        .filter(cast(TargetMonitoringExpiration.deadline_date, Date) <= deadline_day)\
        .filter(TargetMonitoringExpiration.due_date == None)\
        .filter(TargetMonitoringExpiration.responsible_id == user_id)\
        .join(TargetMonitoring, TargetMonitoringExpiration.target_monitoring_id == TargetMonitoring.id)\
        .join(MonitoringCase, MonitoringCase.target_monitoring_id == TargetMonitoring.id)\
        .join(LoanCase, LoanCase.monitoring_case_id == MonitoringCase.id)\
        .join(Loan_Portfolio, LoanCase.loan_portfolio_id == Loan_Portfolio.id)

    
    
    schedule_deadlines = db_session.query(ScheduledMonitoringExpiration, Loan_Portfolio.loan_id)\
        .filter(cast(ScheduledMonitoringExpiration.deadline_date, Date) <= deadline_day)\
        .filter(ScheduledMonitoringExpiration.due_date == None)\
        .filter(ScheduledMonitoringExpiration.responsible_id == user_id)\
        .join(ScheduledMonitoring, ScheduledMonitoringExpiration.scheduled_monitoring_id == ScheduledMonitoring.id)\
        .join(MonitoringCase, MonitoringCase.id == ScheduledMonitoring.id)\
        .join(LoanCase, LoanCase.monitoring_case_id == MonitoringCase.id)\
        .join(Loan_Portfolio, LoanCase.loan_portfolio_id == Loan_Portfolio.id)

    unschedule_deadlines = db_session.query(UnscheduledMonitoringExpiration, Loan_Portfolio.loan_id)\
        .filter(cast(UnscheduledMonitoringExpiration.deadline_date, Date) <= deadline_day)\
        .filter(UnscheduledMonitoringExpiration.due_date == None)\
        .filter(UnscheduledMonitoringExpiration.responsible_id == user_id)\
        .join(UnscheduledMonitoring, UnscheduledMonitoringExpiration.unscheduled_monitoring_id == UnscheduledMonitoring.id)\
        .join(MonitoringCase, MonitoringCase.id == UnscheduledMonitoring.id)\
        .join(LoanCase, LoanCase.monitoring_case_id == MonitoringCase.id)\
        .join(Loan_Portfolio, LoanCase.loan_portfolio_id == Loan_Portfolio.id)
    
    deadlines = target_deadlines.union(schedule_deadlines).union(unschedule_deadlines).order_by(TargetMonitoringExpiration.deadline_date.asc(), Loan_Portfolio.loan_id)
    count = deadlines.count()
    deadlines = deadlines.limit(10).offset(10*page).all()
    
    for deadline in deadlines:
        deadlines_list.append({
            "loan_id": deadline[1],
            "deadline_date": deadline[0].deadline_date.date(),
            "remainder": (deadline[0].deadline_date.date() - today.date()).days,
        })


    return [deadlines_list, count]

