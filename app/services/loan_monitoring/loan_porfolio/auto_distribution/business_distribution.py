import datetime
from .....models.brief_case.directories.loan_product import loan_product
from .....models.brief_case.loan_portfolio import Loan_Portfolio
from .....models.loan_case.loan_case_history_model import LoanCaseHistory
from .....models.problems_case.problems_case_history import ProblemsCaseHistory
from .....models.juridical_case.juridical_case_history_model import JuridicalCaseHistory
from .....models.problems_case.problems_case_model import ProblemsCase
from .....models.juridical_case.juridical_case_model import JuridicalCase
from ...task_manager.task_manager_crud import TaskManager_class
from .....schemas.loan_portfolio_schemas import UserAcceptedLoanData, CreateLoanCase
from ...loan_case import loan_case_crud
from ...monitoring_case import target_monitoring_crud
from .....schemas.notification_schemas import CreateNotification
from ...notification.notification_crud import Notificaton_class
from .....common.dictionaries import notification_dictionary
from app.services.loan_monitoring.problems_case import problems_case_crud
from . import kad_distribution
from . import problem_distribution
from .....models.brief_case.directories.loan_product import loan_product
from ...juridical_case import juridical_case_crud
import time
from sqlalchemy.sql import text
from  app.services.users.users_crud import Users as users
from .....models.users.users import Users as user, user_role
from .....models.users.attached_regions import attached_regions
from .....schemas.task_manager_schemas import UpdateTaskManagerAccept
from .....common.commit import commit_object, flush_object
from .....common.dictionaries.from_type import FromType
from .....common.dictionaries.departments_dictionary import DEP
from .....common.dictionaries.general_tasks_dictionary import JGT, MGT
from .....config.logs_config import cron_logger
from ....business_case import business_case_crud
from ....kad_case import kad_case_crud

from .....common.dictionaries.departments_dictionary import DEP, ROLES
from .....models.business_case.business_case_model import BusinessCase
from sqlalchemy import or_


def uncheck_portfolio(db_session):
    cron_logger.info(f'Started uncheck portfolio for distribution')
    db_session.execute( '''UPDATE LOAN_PORTFOLIO SET CHECKED_STATUS=2 WHERE STATUS=1''' )
    commit_object(db_session)
    cron_logger.info(f'Finished uncheck portfolio for distribution')


def set_false_on_unchecked(db_session):
    cron_logger.info(f'Started set_false_on_unchecked for distribution')
    db_session.execute( '''UPDATE LOAN_PORTFOLIO SET is_taken_business=false, is_taken_kad=false, is_taken_problem=false WHERE STATUS=1 AND CHECKED_STATUS=2''' )
    commit_object(db_session)
    cron_logger.info(f'Finished set_false_on_unchecked for distribution')



def auto_distribution_all(db_session):
    
    uncheck_portfolio(db_session)
    
    portfolio_auto_distribution_by_local_to_businessv1(db_session)
    kad_distribution.portfolio_auto_distribution_by_local_to_kad(db_session)
    problem_distribution.portfolio_auto_distribution_by_local_to_problemv1(db_session)
    
    set_false_on_unchecked(db_session)










def portfolio_auto_distribution_by_local_to_businessv1(db_session):
    start_timer = time.time()
    cron_logger.info(f'Started auto distribution, start_time: {start_timer}')
    get_regions = db_session.query(attached_regions).filter(attached_regions.department_id == DEP.BUSINESS.value).filter(attached_regions.attached_type_id == 1).all()
    regions = [x.region_id for x in get_regions]
    if regions!=[]:
        query = db_session.execute(text(f'''SELECT LP.ID,
                                                    LP.LOCAL_CODE_ID,
                                                    LP.CLIENT_REGION,
                                                    LP.IS_TAKEN_BUSINESS,
                                                    LP.IS_TAKEN_KAD,
                                                    LP.IS_TAKEN_PROBLEM,
                                                    LP.DATE_OVERDUE_PERCENT,
                                                    LP.OVERDUE_START_DATE
                                                    
                            FROM LOAN_PORTFOLIO LP
                            WHERE ((LP.DATE_OVERDUE_PERCENT IS NULL AND LP.OVERDUE_START_DATE IS NOT NULL AND CURRENT_DATE - LP.OVERDUE_START_DATE < 31)
                                OR (LP.OVERDUE_START_DATE IS NULL AND LP.DATE_OVERDUE_PERCENT IS NOT NULL AND CURRENT_DATE - LP.OVERDUE_START_DATE < 31)
                                OR ( LP.DATE_OVERDUE_PERCENT IS NOT NULL AND LP.OVERDUE_START_DATE IS NOT NULL AND
                                            ((LP.OVERDUE_START_DATE < LP.DATE_OVERDUE_PERCENT AND CURRENT_DATE - LP.OVERDUE_START_DATE < 31)
                                        OR (LP.OVERDUE_START_DATE >= LP.DATE_OVERDUE_PERCENT AND CURRENT_DATE - LP.DATE_OVERDUE_PERCENT < 31))))
                                AND LP.BALANCE_95413 IS NULL AND LP.BALANCE_91501 IS NULL AND LP.BALANCE_91503 IS NULL
                                AND (LP.IS_TAKEN_NON_TARGET IS FALSE OR LP.IS_TAKEN_NON_TARGET IS NULL)
                                AND LP.CLIENT_REGION in {tuple(regions)} AND LP.STATUS = 1''')).fetchall()
        
        i=0
        for loan in query:
            
            get_business = db_session.query(BusinessCase).filter(BusinessCase.loan_portfolio_id == loan.id).first()                                                                           
            if get_business is not None:
                print('in get_business is not None')
                if loan.is_taken_business == True:
                    print('in is_taken_business == True')
                    get_business.from_type_id = FromType.TYPE_030.value
                    get_business.checked_status = True
                    get_business.business_case_status_id = 1
                    # db_session.execute(text(f"UPDATE business_case set from_type_id=:from_type, checked_status=true where id=:business_id"),
                    #                 {"from_type":FromType.TYPE_030.value, "business_id":loan.id})
                    # flush_object(db_session)
                elif loan.is_taken_kad == True:
                    print('in is_taken_kad == True')
                    get_business.from_type_id = FromType.TYPE_3160.value
                    get_business.checked_status = True
                    get_business.business_case_status_id = 1
                    # db_session.execute(text(f"UPDATE business_case set from_type_id=:from_type,checked_status=true, business_case_status_id=:case_status where id=:business_id"), 
                    #                 {"from_type":FromType.TYPE_3160.value, "business_id":loan.id, "case_status":1})
                    # is_taken = 'is_taken_kad'
                    
                elif loan.is_taken_problem == True:
                    print('in is_taken_problem == True')
                    get_business.from_type_id = FromType.TYPE_60.value
                    get_business.checked_status = True
                    get_business.business_case_status_id = 1
                    # db_session.execute(text(f"UPDATE business_case set from_type_id=:from_type, checked_status=true,  business_case_status_id=:case_status where id=:business_id"),
                    #                 {"from_type":FromType.TYPE_60.value, "business_id":loan.id, "case_status":1})
                    # is_taken = 'is_taken_problem'
                    
                
                db_session.execute(text(f"UPDATE loan_portfolio set checked_status=1, is_taken_business=true, is_taken_kad=false, is_taken_problem=false where id = {loan['id']}"))
                    
            else:
                print('in else')
                from_type = FromType.NEW.value
                if loan.is_taken_kad == True:
                    # is_taken = 'is_taken_kad'
                    from_type = FromType.TYPE_3160.value
                elif loan.is_taken_problem == True:
                    # is_taken = 'is_taken_problem'
                    from_type = FromType.TYPE_60.value
                get_attached_user = db_session.query(attached_regions).filter(attached_regions.region_id == loan.client_region)\
                    .filter(attached_regions.department_id == DEP.BUSINESS.value).first()
                get_second_user = db_session.query(user).filter(user.local_code == loan['local_code_id']).filter(user.department == DEP.BUSINESS.value)\
                        .join(user_role).filter(user_role.columns.role_id == ROLES.business_block_filial_admin.value).first()
                if get_attached_user is not None and get_second_user is not None:
                    print('get_attached_user is not None and get_second_user is not None')
                    task = TaskManager_class()
                    new_task = task.create_task_manager_when_business_user_accept_loan(db_session)
                    flush_object(db_session)
                    
                    case_data = CreateLoanCase()
                    case_data.loan_portfolio_id = loan['id']
                    case_data.main_responsible_id = get_attached_user.user_id
                    case_data.second_responsible_id = get_second_user.id
                    business_case_crud.create_business_case_with_append_task(new_task, case_data, from_type, db_session)
                    
                    data = UpdateTaskManagerAccept()
                    data.task_manager_id = new_task.id
                    task = TaskManager_class(data)
                    task.loan_case_task_manager_set_on_work(db_session)
                    
                    db_session.execute(text(f"UPDATE loan_portfolio set checked_status=1, is_taken_business=true, is_taken_kad=false, is_taken_problem=false where id = {loan['id']}"))
            
            
            i=i+1
                    
            if i % 10000 == 0:
                
                cron_logger.info(f'Commited {i} loan_case elements')
                commit_object(db_session)
   
       
    commit_object(db_session)
    end_timer = time.time()
    res = end_timer - start_timer
    final_res = res / 60
    cron_logger.info(f'Finished auto distribution business case, Execution time: {final_res} minutes')
    return 'OK'






def close_business_case(db_session):
    get_business = db_session.query(BusinessCase).filter(BusinessCase.checked_status == False).update(BusinessCase.business_case_status_id == 2).all()
    
    