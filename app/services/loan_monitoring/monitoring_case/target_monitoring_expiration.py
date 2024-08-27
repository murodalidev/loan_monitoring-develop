from sqlalchemy.sql import text
import datetime
from sqlalchemy import  and_, cast, Date
import sqlalchemy
import datetime
import calendar
from dateutil.relativedelta import relativedelta
from ....models.brief_case.directories.loan_product import loan_product
from ....models.monitoring_case.monitoring_case_model import MonitoringCase
from ....models.problems_case.problems_case_model import ProblemsCase
from ....models.juridical_case.juridical_case_model import JuridicalCase
from ....models.monitoring_case.target_monitoring_expiration_model import TargetMonitoringExpiration
from ....models.monitoring_case.unscheduled_monitoring.unscheduled_monitoring_expiration_model import UnscheduledMonitoringExpiration
from ....models.monitoring_case.unscheduled_monitoring.unscheduled_monitoring_model import UnscheduledMonitoring
from ....models.monitoring_case.scheduled_monitoring_expiration_model import ScheduledMonitoringExpiration
from ....models.monitoring_case.target_monitoring_model import TargetMonitoring
from ....models.monitoring_case.scheduled_monitoring_model import ScheduledMonitoring
from ....models.monitoring_task_manager.task_manager_model import TaskManager
from ....models.brief_case.loan_portfolio import Loan_Portfolio
from ..task_manager.task_manager_crud import TaskManager_class
from ....models.loan_case.loan_case_model import LoanCase
from ....services.loan_monitoring.monitoring_case import scheduled_monitoring_crud, target_monitoring_crud
from ....common.dictionaries.monitoring_case_dictionary import loan_case
from ..loan_case import loan_case_crud
from ....common.is_empty import  is_empty_list, is_exists
from ....common.commit import commit_object, flush_object
from sqlalchemy import or_
from ....common.dictionaries.departments_dictionary import DEP
from ....common.dictionaries.general_tasks_dictionary import JGT, MGT, PGT, GTCAT
from ....config.logs_config import cron_logger


def get_target_expirations_for_user(user_id, db_session):
    
    return {'target_monitoring_expiration': query('target_monitoring_expiration', user_id, db_session),
            'scheduled_monitoring_expiration':query('scheduled_monitoring_expiration', user_id, db_session),
            'unscheduled_monitoring_expiration':query('unscheduled_monitoring_expiration', user_id, db_session)}





def query(expiration, user_id, db_session):
    expirat = []
    get_expiration = db_session.execute(text(f'''SELECT
        EXTRACT(MONTH FROM deadline_date) AS  month,
            EXTRACT(YEAR FROM deadline_date) as year,
        COUNT(id) AS count
        
    FROM {expiration}
    WHERE responsible_id = {user_id}
    AND DATE_PART('year',age(CURRENT_DATE, deadline_date)) < 1
    GROUP BY  EXTRACT(MONTH FROM deadline_date), EXTRACT(YEAR FROM deadline_date)
    order by EXTRACT(MONTH FROM deadline_date) ASC''')).fetchall()
    for expiration in get_expiration:
            expirat.append({"month": int(expiration[0]),
                            "year": int(expiration[1]),
                            "count": int(expiration[2])})
    return expirat




def set_monitoring_expired(db_session):
    cron_logger.info('started terget_set_expired script')
    set_loan_case_expired(TargetMonitoring, TargetMonitoringExpiration, 1, db_session)
    cron_logger.info('started scheduled_set_expired script')
    set_loan_case_expired(ScheduledMonitoring, ScheduledMonitoringExpiration, 2, db_session)
    cron_logger.info('started unscheduled_set_expired script')
    set_loan_case_expired(UnscheduledMonitoring, UnscheduledMonitoringExpiration, 3, db_session)



def set_loan_case_expired(Model, ModelExpiration, monitoring_type, db_session):
    
    get_loan_case = db_session.query(LoanCase, Model).join(MonitoringCase, MonitoringCase.id == LoanCase.monitoring_case_id)
        
    if monitoring_type == 1:
        get_loan_case =get_loan_case.filter(MonitoringCase.target_monitoring_id == Model.id)\
            .filter(Model.target_monitoring_result_id == None)
    elif monitoring_type == 2:
        get_loan_case =get_loan_case.filter(MonitoringCase.id == Model.monitoring_case_id)\
            .filter(Model.scheduled_monitoring_result_id == None)
    elif monitoring_type == 3:
        get_loan_case =get_loan_case.filter(MonitoringCase.id == Model.monitoring_case_id)\
            .filter(Model.unscheduled_monitoring_result_id == None)
    
        
    get_loan_case =get_loan_case.all()
    
    for loan_case, target in get_loan_case:
        check_time = datetime.datetime.now()
        if type(target.deadline) == datetime.date:
            check_time = datetime.datetime.now().date()
        new_expired = None
        if target.deadline < check_time:
            if monitoring_type == 1:
                if loan_case.target_deadline_extension_status_id == 1:
                    loan_case.target_deadline_extension_status_id = 2
                    new_expired = ModelExpiration(responsible_id = loan_case.second_responsible_id,
                                                     target_monitoring_id = target.id,
                                                     deadline_date = target.deadline,
                                                     created_at = datetime.datetime.now())
            elif monitoring_type == 2:
                if loan_case.scheduled_deadline_extension_status_id == 1:
                    loan_case.scheduled_deadline_extension_status_id = 2
                    new_expired = ModelExpiration(responsible_id = loan_case.second_responsible_id,
                                                     scheduled_monitoring_id = target.id,
                                                     deadline_date = target.deadline,
                                                     created_at = datetime.datetime.now())
            elif monitoring_type == 3:
                if loan_case.unscheduled_deadline_extension_status_id == 1:
                    loan_case.unscheduled_deadline_extension_status_id = 2
                    new_expired = ModelExpiration(responsible_id = loan_case.second_responsible_id,
                                                     unscheduled_monitoring_id = target.id,
                                                     deadline_date = target.deadline,
                                                     created_at = datetime.datetime.now())
            
            if new_expired is not None:
                db_session.add(new_expired)
            db_session.add(loan_case)
            flush_object(db_session)
    commit_object(db_session)
    return "OK"




def get_target_expirations_for_user_detail(page, size, user_id, month, db_session):
    get_target_expiration_query = target_expiration_query(user_id, month, db_session)
    get_result  = get_count_and_paginating(get_target_expiration_query, size, page)
    return make_expiration_object(get_result, page, size)


def get_scheduled_expirations_for_user_detail(page, size, user_id, month, db_session):
    get_scheduled_expiration_query = scheduled_expiration_query(user_id, month, db_session)
    get_result  = get_count_and_paginating(get_scheduled_expiration_query, size, page)
    return make_expiration_object(get_result, page, size)

def get_unscheduled_expirations_for_user_detail(page, size, user_id, month, db_session):
    get_unscheduled_expiration_query = unscheduled_expiration_query(user_id, month, db_session)
    get_result  = get_count_and_paginating(get_unscheduled_expiration_query, size, page)
    return make_expiration_object(get_result, page, size)

def get_all_expirations_for_user_detail(page, size, user_id, month, db_session):
    get_unscheduled_expiration_query = unscheduled_expiration_query(user_id, month, db_session)
    get_scheduled_expiration_query = scheduled_expiration_query(user_id, month, db_session)
    get_target_expiration_query = target_expiration_query(user_id, month, db_session)
    get_expirations = get_target_expiration_query.union(get_unscheduled_expiration_query).union(get_scheduled_expiration_query)
    get_result  = get_count_and_paginating(get_expirations, size, page)
    return make_expiration_object(get_result, page, size)






def target_expiration_query(user_id, month, db_session):
    date_period = get_date_period(month)
    get_expirations = db_session.query(TargetMonitoringExpiration, LoanCase)\
        .join(MonitoringCase, MonitoringCase.target_monitoring_id == TargetMonitoringExpiration.target_monitoring_id)\
            .join(LoanCase, LoanCase.monitoring_case_id == MonitoringCase.id)\
                .filter(TargetMonitoringExpiration.responsible_id == user_id)\
                    .filter(and_((cast(TargetMonitoringExpiration.deadline_date, Date) >= date_period[0]),(cast(TargetMonitoringExpiration.deadline_date, Date) <= date_period[1])))
    return get_expirations
    


def scheduled_expiration_query(user_id, month, db_session):
    date_period = get_date_period(month)
    get_expirations = db_session.query(ScheduledMonitoringExpiration, LoanCase)\
    .join(ScheduledMonitoring, ScheduledMonitoring.id == ScheduledMonitoringExpiration.scheduled_monitoring_id)\
        .join(MonitoringCase, MonitoringCase.id == ScheduledMonitoring.monitoring_case_id)\
            .join(LoanCase, LoanCase.monitoring_case_id == MonitoringCase.id)\
                    .filter(ScheduledMonitoringExpiration.responsible_id == user_id)\
                        .filter(and_((cast(ScheduledMonitoringExpiration.deadline_date, Date) >= date_period[0]),(cast(ScheduledMonitoringExpiration.deadline_date, Date) <= date_period[1])))
    return get_expirations


def unscheduled_expiration_query(user_id, month, db_session):
    date_period = get_date_period(month)
    get_expirations = db_session.query(UnscheduledMonitoringExpiration, LoanCase)\
        .join(UnscheduledMonitoring, UnscheduledMonitoring.id == UnscheduledMonitoringExpiration.unscheduled_monitoring_id)\
            .join(MonitoringCase, MonitoringCase.id == UnscheduledMonitoring.monitoring_case_id)\
                .join(LoanCase, LoanCase.monitoring_case_id == MonitoringCase.id)\
                        .filter(UnscheduledMonitoringExpiration.responsible_id == user_id)\
                            .filter(and_((cast(UnscheduledMonitoringExpiration.deadline_date, Date) >= date_period[0]),(cast(UnscheduledMonitoringExpiration.deadline_date, Date) <= date_period[1])))
    return get_expirations






def get_date_period(month):
    mon = f'{datetime.datetime.now().year} {calendar.month_name[month]}'
    start_date = datetime.datetime.strptime(mon, "%Y %B").date()
    end_date = start_date + relativedelta(day=31)
    
    return start_date, end_date
    
    
def get_count_and_paginating(get_expirations, size, page):
    
    count = get_expirations.count()
    get_expirations = get_expirations.limit(size).offset((page-1)*size).all()
    return get_expirations, count



def make_expiration_object(get_expiration_query, page, size):
    personal_expirations = []
    for expiration, loan_case in get_expiration_query[0]:
         end_date = expiration.due_date and expiration.due_date or datetime.datetime.today()

         personal_expirations.append({
              "loan_client": f'{loan_case.portfolio.loan_id}: {loan_case.portfolio.client_name}',
              "loan_case_id": loan_case.id,
              "loan_portfolio_id": loan_case.portfolio.id,
              "deadline_date": expiration.deadline_date,
              "due_date": expiration.due_date,
              "count": (end_date - expiration.deadline_date).days
         })
    return {"items": personal_expirations,
            "total":get_expiration_query[1],
            "page":page,
            "size":size}