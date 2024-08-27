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
from .....common.dictionaries.departments_dictionary import DEP, ROLES
from .....common.dictionaries.general_tasks_dictionary import JGT, MGT
from .....config.logs_config import cron_logger
from ....business_case import business_case_crud
from ....kad_case import kad_case_crud
from .....models.business_case.business_case_model import BusinessCase
from .....models.kad_case.kad_case_model import KADCase
from sqlalchemy import or_




 
 
 
 
 
def portfolio_auto_distribution_by_local_to_kad(db_session):
    start_timer = time.time()
    is_taken = None
    cron_logger.info(f'Started auto distribution, start_time: {start_timer}')
    get_regions = db_session.query(attached_regions).filter(attached_regions.department_id == DEP.KAD.value).filter(attached_regions.attached_type_id == 2).all()
    regions = [x.region_id for x in get_regions]
    if regions is not None:
        get_loans = db_session.execute(text(f'''SELECT LP.ID,
                                                LP.LOCAL_CODE_ID,
                                                LP.CLIENT_REGION,
                                                LP.IS_TAKEN_KAD,
                                                LP.IS_TAKEN_BUSINESS,
                                                LP.IS_TAKEN_PROBLEM,
                                                LP.DATE_OVERDUE_PERCENT,
                                                LP.OVERDUE_START_DATE
                                            FROM LOAN_PORTFOLIO LP
                                            
                                            WHERE ((LP.DATE_OVERDUE_PERCENT IS NULL
                                                    AND LP.OVERDUE_START_DATE IS NOT NULL
                                                    AND (CURRENT_DATE - LP.OVERDUE_START_DATE >= 31
                                                    AND CURRENT_DATE - LP.OVERDUE_START_DATE < 61))
                                            OR (LP.OVERDUE_START_DATE IS NULL
                                                    AND LP.DATE_OVERDUE_PERCENT IS NOT NULL
                                                    AND (CURRENT_DATE - LP.DATE_OVERDUE_PERCENT >= 31
                                                    AND CURRENT_DATE - LP.DATE_OVERDUE_PERCENT < 61))
                                            OR (LP.DATE_OVERDUE_PERCENT IS NOT NULL
                                                    AND LP.OVERDUE_START_DATE IS NOT NULL
                                                    AND LP.OVERDUE_START_DATE < LP.DATE_OVERDUE_PERCENT
                                                    AND (CURRENT_DATE - LP.OVERDUE_START_DATE >= 31
                                                    AND CURRENT_DATE - LP.OVERDUE_START_DATE < 61))
                                            OR (LP.DATE_OVERDUE_PERCENT IS NOT NULL
                                                    AND LP.OVERDUE_START_DATE IS NOT NULL
                                                    AND LP.OVERDUE_START_DATE >= LP.DATE_OVERDUE_PERCENT
                                                    AND (CURRENT_DATE - LP.DATE_OVERDUE_PERCENT >= 31
                                                    AND CURRENT_DATE - LP.DATE_OVERDUE_PERCENT < 61)))
                                            AND LP.BALANCE_95413 IS NULL AND LP.BALANCE_91501 IS NULL AND LP.BALANCE_91503 IS NULL
                                            AND LP.CLIENT_REGION in :tuple
                                            AND LP.STATUS = :status'''), {"tuple":tuple(regions), "status":1}).fetchall()
        
        i=0
        print(len(get_loans))
        for loan in get_loans:
            
            get_kad = db_session.query(KADCase).filter(KADCase.loan_portfolio_id == loan.id).first()
            if get_kad is not None:
                if loan.is_taken_kad == True:
                    print('in is_taken_kad == True')
                    get_kad.from_type_id = FromType.TYPE_3160.value
                    get_kad.checked_status = True
                    get_kad.kad_case_status_id = 1
                    # db_session.execute(text(f"UPDATE kad_case set from_type_id=:from_type,checked_status=true, kad_case_status_id=:case_status where id=:kad_id"), 
                    #                 {"from_type":FromType.TYPE_3160.value, "kad_id":loan.id, "case_status":1})
                elif loan.is_taken_business == True:
                    print('in is_taken_business == True')
                    get_kad.from_type_id = FromType.TYPE_030.value
                    get_kad.checked_status = True
                    get_kad.kad_case_status_id = 1
                    # db_session.execute(text(f"UPDATE kad_case set from_type_id=:from_type, checked_status=true where id=:kad_id"),
                    #                     {"from_type":FromType.TYPE_030.value, "kad_id":loan.id})
                    #is_taken = 'is_taken_business'
                elif loan.is_taken_problem == True:
                    print('in is_taken_problem == True')
                    get_kad.from_type_id = FromType.TYPE_60.value
                    get_kad.checked_status = True
                    get_kad.kad_case_status_id = 1
                    # db_session.execute(text(f"UPDATE kad_case set from_type_id=:from_type, checked_status=true,  kad_case_status_id=:case_status where id=:kad_id"),
                    #                 {"from_type":FromType.TYPE_60.value, "kad_id":loan.id, "case_status":1})
                    #is_taken = 'is_taken_problem'
                    
                db_session.execute(text(f"UPDATE loan_portfolio set checked_status=1, is_taken_kad=true, is_taken_problem=false, is_taken_business=false where id = {loan['id']}"))
            
            else:
                print('in else')
                from_type = FromType.NEW.value
                if loan.is_taken_business == True:
                    from_type = FromType.TYPE_030.value
                    #is_taken = 'is_taken_business'
                elif loan.is_taken_problem == True:
                    from_type = FromType.TYPE_60.value
                    #is_taken = 'is_taken_problem'
                i=i+1
                
                get_attached_user = db_session.query(attached_regions).filter(attached_regions.region_id == loan.client_region)\
                    .filter(attached_regions.department_id == DEP.KAD.value).first()
                
                get_second_user = db_session.query(user).filter(user.local_code == loan.local_code_id)\
                    .filter(user.department == DEP.KAD.value)\
                        .join(user_role).filter(user_role.columns.role_id == ROLES.kad_block_filial_admin.value).first()
                if get_attached_user is not None and get_second_user is not None:
                    print('in get_attached_user is not None and get_second_user is not None')
                    task = TaskManager_class()
                    new_task = task.create_task_manager_when_kad_user_accept_loan(db_session)
                    flush_object(db_session)
                    case_data = CreateLoanCase()
                    case_data.loan_portfolio_id = loan.id
                    case_data.main_responsible_id = get_attached_user.user_id
                    case_data.second_responsible_id = get_second_user.id
                    kad_case_crud.create_kad_case_with_append_task(new_task, case_data,from_type, db_session)
                                
                    db_session.execute(text(f"UPDATE loan_portfolio set checked_status=1, is_taken_kad=true, is_taken_problem=false, is_taken_business=false where id = {loan['id']}"))
                    
                                
                        
                if i % 10000 == 0:
                    cron_logger.info(f'Commited {i} loan_case elements')
                    commit_object(db_session)
  
       
    commit_object(db_session)
    end_timer = time.time()
    res = end_timer - start_timer
    final_res = res / 60
    cron_logger.info(f'Finished auto distribution kad case, Execution time: {final_res} minutes')
    return 'OK'