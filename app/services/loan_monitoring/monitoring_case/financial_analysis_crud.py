import datetime
from ....models.monitoring_case.financial_analysis_model import FinancialAnalysis
from ....models.loan_case.loan_case_model import LoanCase
from ....models.loan_case.loan_case_history_model import LoanCaseHistory
from ....models.monitoring_case.scheduled_monitoring_model import ScheduledMonitoring
from ....models.statuses.financial_analysis_status_model import FinancialAnalysisStatus
from ....common.is_empty import  is_exists
from ....common.commit import commit_object, flush_object
from ..task_manager.task_manager_crud import TaskManager_class
from ....common.dictionaries.monitoring_case_dictionary import monitoring_status
from ....common.dictionaries.notification_dictionary import notification_type, notification_body
from ....common.dictionaries.case_history_dictionaries import loan_case_history
from ....schemas.task_manager_schemas import CreateTaskManagerSetTargetMonitoring
from ..notification.notification_crud import Notificaton_class
from ....schemas.notification_schemas import CreateNotification
from ....common.dictionaries.departments_dictionary import DEP
from ....common.dictionaries.general_tasks_dictionary import JGT, MGT, PGT, GTCAT

def create_financial_analyse(request, db_session):
    count_finanl = db_session.query(FinancialAnalysis).filter(FinancialAnalysis.monitoring_case_id == request.monitoring_case_id).count()
    
    new_fin_analyse = FinancialAnalysis(
        monitoring_case_id = request.monitoring_case_id and request.monitoring_case_id or None, 
        income_plan = request.income_plan and request.income_plan or None,
        income_fact = request.income_fact and request.income_fact or None,
        profit_plan = request.profit_plan and request.profit_plan or None,
        profit_fact = request.profit_fact and request.profit_fact or None,
        expences_plan = request.expences_plan and request.expences_plan or None,
        expences_fact = request.expences_fact and request.expences_fact or None,
        net_profit_plan = request.net_profit_plan and request.net_profit_plan or None,
        net_profit_fact = request.net_profit_fact and request.net_profit_fact or None,
        new_workplaces_plan = request.new_workplaces_plan and request.new_workplaces_plan or None,
        new_workplaces_fact = request.new_workplaces_fact and request.new_workplaces_fact or None,
        created_at = datetime.datetime.now(),
        financial_analysis_status_id = request.financial_analysis_status_id,
        year = count_finanl + 1,
    )

    db_session.add(new_fin_analyse)
    
    new_loan_case_history = LoanCaseHistory(loan_case_id = request.loan_case_id, 
                                            general_task_id = MGT.FINAN.value,
                                            from_user_id = request.from_user, 
                                            comment = request.comment and request.comment or None,
                                            created_at = datetime.datetime.now(),
                                            message = loan_case_history['financial_analysis']
                                                )
    db_session.add(new_loan_case_history)
    commit_object(db_session)
    
    return {"OK"}





def update_financial_analyse(id, request, db_session):
    finanl = db_session.query(FinancialAnalysis).filter(FinancialAnalysis.id == id).first()
    
    if request.income_plan is not None:
        finanl.income_plan = request.income_plan
    if request.income_fact is not None:
        finanl.income_fact = request.income_fact
    if request.profit_plan is not None:
        finanl.profit_plan = request.profit_plan
    if request.profit_fact is not None:
        finanl.profit_fact = request.profit_fact
    if request.expences_plan is not None:
        finanl.expences_plan = request.expences_plan
    if request.expences_fact is not None:
        finanl.expences_fact = request.expences_fact
    if request.net_profit_plan is not None:
        finanl.net_profit_plan = request.net_profit_plan
    if request.net_profit_fact is not None:
        finanl.net_profit_fact = request.net_profit_fact
    if request.new_workplaces_plan is not None:
        finanl.new_workplaces_plan = request.new_workplaces_plan
    if request.new_workplaces_fact is not None:
        finanl.new_workplaces_fact = request.new_workplaces_fact
    finanl.updated_at = datetime.datetime.now()
    
    commit_object(db_session)
    
    return {"OK"}




def get_financial_analysis(monitoring_case_id, db_session):
    get_finanl = db_session.query(FinancialAnalysis).filter(FinancialAnalysis.monitoring_case_id == monitoring_case_id)\
        .order_by(FinancialAnalysis.id.asc()).all()
    is_exists(get_finanl, 400, 'Financial analise not found')
    finanl = []
    for fin in get_finanl:
        finanl.append({"id": fin.id,
                "income_plan": fin.income_plan and fin.income_plan or None,
                "income_fact": fin.income_fact and fin.income_fact or None,
                "profit_plan": fin.profit_plan and fin.profit_plan or None,
                "profit_fact": fin.profit_fact and fin.profit_fact or None,
                "expences_plan": fin.expences_plan and fin.expences_plan or None,
                "expences_fact": fin.expences_fact and fin.expences_fact or None,
                "net_profit_plan": fin.net_profit_plan and fin.net_profit_plan or None,
                "net_profit_fact": fin.net_profit_fact and fin.net_profit_fact or None,
                "new_workplaces_plan": fin.new_workplaces_plan and fin.new_workplaces_plan or None,
                "new_workplaces_fact": fin.new_workplaces_fact and fin.new_workplaces_fact or None,
                "created_at": fin.created_at and fin.created_at or None,
                "updated_at": fin.updated_at and fin.updated_at or None,
                "financial_analysis_status_id": fin.financial_analysis_status_id and fin.financial_analysis_status_id,
                "year": fin.year and fin.year or None
                                 })
        
    return finanl
    



def get_final_status(db_session):
    statuses = []
    status = db_session.query(FinancialAnalysisStatus).all()

    for stat in status:
        statuses.append({'id':stat.id,
                         'name':stat.name,
                         'code':stat.code})
        
    return status
        





def appoint_scheduled_monitoring(request, db_session):
    
    data = CreateTaskManagerSetTargetMonitoring()
    data.general_task_id = request.general_task_id
    task = TaskManager_class(data)
    new_task = task.create_task_manager_when_set_scheduled_monitoring(db_session)
    
    new_scheduled_monitoring = ScheduledMonitoring(monitoring_case_id = request.monitoring_case_id,
                                             scheduled_monitoring_status_id = monitoring_status['назначен'],
                                             frequency_period_id = request.frequency_period_id,
                                             task_manager_id = new_task.id,
                                             created_at = datetime.datetime.now())
    
    db_session.add(new_scheduled_monitoring)
    flush_object(db_session)
    
    
    
    get_loan_case = db_session.query(LoanCase).filter(LoanCase.id == request.loan_case_id).first()
    data = CreateNotification()
    data.from_user_id = request.main_responsible_id
    data.to_user_id = request.second_responsible_id
    data.notification_type = notification_type['scheduled_monitoring']
    data.body = notification_body['appoint_scheduled_monitoring']
    data.url = f'{get_loan_case.loan_portfolio_id}' + ':' + f'{get_loan_case.id}'
    
    notifiaction = Notificaton_class(data)
    notifiaction.create_notification(db_session)
    
    new_loan_case_history = LoanCaseHistory(loan_case_id = request.loan_case_id, 
                                            general_task_id = request.general_task_id,
                                            from_user_id = request.main_responsible_id, 
                                            to_user_id= request.second_responsible_id,
                                            comment = request.comment,
                                            created_at = datetime.datetime.now(),
                                            message = loan_case_history['appoint_scheduled']
                                                )
    db_session.add(new_loan_case_history)
    
    
    
    commit_object(db_session)
    
    return {"OK"}



