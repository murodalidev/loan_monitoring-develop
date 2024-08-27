import datetime
from app.models.brief_case.directories.local_code import local_code
from app.models.loan_case.loan_case_model import LoanCase
from app.models.monitoring_case.monitoring_case_model import MonitoringCase
from app.models.users.attached_regions import attached_regions
from ....models.brief_case.directories.loan_product import loan_product
from ....models.brief_case.loan_portfolio import Loan_Portfolio
from ..task_manager.task_manager_crud import TaskManager_class
from ....schemas.loan_portfolio_schemas import  CreateLoanCase
from ..loan_case import loan_case_crud
from ..monitoring_case import target_monitoring_crud
from ....schemas.notification_schemas import CreateNotification
from ..notification.notification_crud import Notificaton_class
from ....common.dictionaries import notification_dictionary
from ....models.brief_case.directories.loan_product import loan_product
import time
from ....common.decorator import measure_time
from ....models.users.users import Users as user, user_role
from ....models.users.attached_branches import attached_branches
from ....schemas.task_manager_schemas import UpdateTaskManagerAccept
from ....common.commit import commit_object, flush_object
from ....common.dictionaries.general_tasks_dictionary import  MGT
from ....common.dictionaries.departments_dictionary import  ROLES, DEP
from ....config.logs_config import cron_logger


def portfolio_auto_distribution_by_local(db_session, is_new_local=None):
    start_timer = time.time()
    cron_logger.info(f'Started auto distribution, start_time: {start_timer}')
    locals = None
    if is_new_local is not None:
            get_locals = db_session.query(local_code).filter(local_code.status ==False).all()
            locals = [x.region_id for x in get_locals]
        
    get_loans = db_session.query(Loan_Portfolio).filter(Loan_Portfolio.status == 1)\
        .filter(Loan_Portfolio.total_overdue != None)
    
    if locals is not None:    
        get_loans = get_loans.filter(Loan_Portfolio.local_code_id.in_(locals))
    
    get_loans = get_loans.all()
    
    i=0
    for loan in get_loans:
        i=i+1
        get_attached_user = db_session.query(attached_regions).filter(attached_regions.region_id == loan.client_region)\
            .filter(attached_regions.department_id == DEP.KAD.value).filter(user.id == user_role.columns.user_id)\
                    .join(user_role, user_role.columns.role_id == ROLES.monitoring_main_admin.value).first()
            
        get_second_user = db_session.query(user).filter(user.local_code == loan.local_code_id)\
            .filter(user.department == DEP.KAD.value).join(user_role).filter(user_role.columns.role_id == ROLES.monitoring_filial_admin.value).first()
        if get_attached_user is not None and get_second_user is not None:
            if loan.loan_product is not None:
                get_loan_product = db_session.query(loan_product).filter(loan_product.name == loan.loan_product).first()
                if get_loan_product is not None:
                    if get_loan_product.is_target is not None:
                        get_local = db_session.query(local_code).filter(local_code.id ==loan.local_code_id).first()
                        if get_local.status == False:
                            get_local.status == True
                        get_loan_case = db_session.query(LoanCase).filter(LoanCase.loan_portfolio_id == loan.id).first()
                        if get_loan_case is not None:
                            if get_loan_case.monitoring_case.monitoring_case_status_id==2 and get_loan_product.is_target == 1:
                                get_loan_case.monitoring_case.monitoring_case_status_id=1
                                
                            if get_loan_case.monitoring_case.target_monitoring_id is None:
                                target_monitoring_crud.appoint_target_monitoring_list_tasks(get_loan_case.monitoring_case, MGT.TARGET_MONITORING.value, get_attached_user.user_id, get_second_user.id, db_session)
                            loan.is_taken_loan = True
                        else:
                        
                            task = TaskManager_class()
                            new_task = task.create_task_manager_when_user_accept_loan(db_session)
                            flush_object(db_session)
                            case_data = CreateLoanCase()
                            case_data.loan_portfolio_id = loan.id
                            case_data.main_responsible_id = get_attached_user.user_id
                            case_data.second_responsible_id = get_second_user.id
                            new_loan_case = loan_case_crud.create_loan_case_with_append_task(new_task, case_data, db_session)
                            
                            monitoring_case = loan_case_crud.appoint_responsible_list_tasks(new_loan_case, db_session)
                            
                            
                            
                            if get_loan_product.is_target == 0:
                                data = UpdateTaskManagerAccept()
                                data.task_manager_id = new_task.id
                                task = TaskManager_class(data)
                                task.loan_case_task_manager_set_on_work(db_session)
                            else:
                                target_monitoring_crud.appoint_target_monitoring_list_tasks(monitoring_case, MGT.TARGET_MONITORING.value, get_attached_user.user_id, get_second_user.id, db_session)
                            loan.is_taken_loan = True
                        flush_object(db_session)
                else:
                    new_loan_product = loan_product(name = str(loan.loan_product).replace(" ", ""), created_at=datetime.datetime.now())
                    db_session.add(new_loan_product)
                    flush_object(db_session)
                    
                        
                   
        if i % 1000 == 0:
            cron_logger.info(f'Commited {i} loan_case elements')
            commit_object(db_session)
            
    commit_object(db_session)
    end_timer = time.time()
    res = end_timer - start_timer
    final_res = res / 60
    cron_logger.info(f'Finished auto distribution, Execution time: {final_res} minutes')
    return 'OK'





def check_loan_case_with_product_change(db_session):
    start_timer = time.time()
    cron_logger.info(f'Started check_loan_case_with_product_change, start_time: {start_timer}')
    get_loan_products = db_session.query(loan_product).filter(loan_product.is_target==0).all()
    
    for product in get_loan_products:
        get_monitoring_case = db_session.query(MonitoringCase).join(LoanCase, LoanCase.monitoring_case_id == MonitoringCase.id).join(Loan_Portfolio, Loan_Portfolio.id == LoanCase.loan_portfolio_id)\
            .filter(Loan_Portfolio.loan_product == product.name).all()
            
        
        for monitoring in get_monitoring_case:
            monitoring.monitoring_case_status_id = 2
            
            flush_object(db_session)
    
    commit_object(db_session)
    end_timer = time.time()
    res = end_timer - start_timer
    final_res = res / 60
    cron_logger.info(f'Finished check_loan_case_with_product_change, Execution time: {final_res} minutes')
    return "OK"
