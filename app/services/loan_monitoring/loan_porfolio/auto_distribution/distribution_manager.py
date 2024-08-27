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
from .....models.users.attached_branches import attached_branches
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
from .....models.users.attached_branches import attached_branches
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
from .....common.decorator import measure_time
from  app.services.users.users_crud import Users as users
from .....models.users.users import Users as user, user_role
from .....models.users.attached_branches import attached_branches
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
from abc import ABC

class DistributionManager(ABC):
    
    def __init__(self, db_session) -> None:
        self.db_session = db_session
    
    
    def distribute_loan():
        pass



class LoanDistrubition():
    
    def __init__(self, distributor:DistributionManager, db_session) -> None:
        self.distributor = distributor
        self.db_session = db_session
    
    def distribute_loans(self):
        return self.distributor.distribute_loan()    
        
    @measure_time
    def uncheck_portfolio(self):
        self.db_session.execute( '''UPDATE LOAN_PORTFOLIO SET CHECKED_STATUS=2 WHERE STATUS=1''' )
        commit_object(self.db_session)
        
        
    @measure_time
    def set_false_on_unchecked(self):
        self.db_session.execute( '''UPDATE LOAN_PORTFOLIO SET is_taken_business=false, is_taken_kad=false, is_taken_problem=false WHERE STATUS=1 AND CHECKED_STATUS=2''' )
        commit_object(self.db_session)








class BusinessDistribution(DistributionManager):
    def __init__(self, db_session) -> None:
        super().__init__(db_session)
    
    @measure_time
    def distribute_loan(self):
        get_locals = self.db_session.query(attached_branches).filter(attached_branches.department_id == DEP.BUSINESS.value).filter(attached_branches.attached_type_id == 1).all()
        locals = [x.local_code_id for x in get_locals]
        query = self.db_session.execute(text(f'''SELECT LP.ID,
                                                    LP.LOCAL_CODE_ID,
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
                                AND LP.LOCAL_CODE_ID in {tuple(locals)} AND LP.STATUS = 1''')).fetchall()
        
        i=0
        for loan in query:
            self.db_session.execute(text(f"UPDATE loan_portfolio set checked_status=1, is_taken_business=true where id = {loan['id']}"))
            get_business = self.db_session.query(BusinessCase).filter(BusinessCase.loan_portfolio_id == loan.id).first()                                                                           
            if get_business is not None:
                print('in get_business is not None')
                if loan.is_taken_business == True:
                    print('in is_taken_business == True')
                    get_business.from_type_id = FromType.TYPE_030.value
                    get_business.checked_status = True
                    get_business.business_case_status_id = 1
                elif loan.is_taken_kad == True:
                    print('in is_taken_kad == True')
                    get_business.from_type_id = FromType.TYPE_3160.value
                    get_business.checked_status = True
                    get_business.business_case_status_id = 1
                    
                elif loan.is_taken_problem == True:
                    print('in is_taken_problem == True')
                    get_business.from_type_id = FromType.TYPE_60.value
                    get_business.checked_status = True
                    get_business.business_case_status_id = 1
                    
            else:
                print('in else')
                from_type = FromType.NEW.value
                if loan.is_taken_kad == True:
                    from_type = FromType.TYPE_3160.value
                elif loan.is_taken_problem == True:
                    from_type = FromType.TYPE_60.value
                get_attached_user = self.db_session.query(attached_branches).filter(attached_branches.local_code_id == loan.local_code_id)\
                    .filter(attached_branches.department_id == DEP.BUSINESS.value).first()
                get_second_user = self.db_session.query(user).filter(user.local_code == loan['local_code_id']).filter(user.department == DEP.BUSINESS.value)\
                        .join(user_role).filter(user_role.columns.role_id == ROLES.business_block_filial_admin.value).first()
                if get_attached_user is not None and get_second_user is not None:
                    print('get_attached_user is not None and get_second_user is not None')
                    task = TaskManager_class()
                    new_task = task.create_task_manager_when_business_user_accept_loan(self.db_session)
                    flush_object(self.db_session)
                    
                    case_data = CreateLoanCase()
                    case_data.loan_portfolio_id = loan['id']
                    case_data.main_responsible_id = get_attached_user.user_id
                    case_data.second_responsible_id = get_second_user.id
                    business_case_crud.create_business_case_with_append_task(new_task, case_data, from_type, self.db_session)
                    
                    data = UpdateTaskManagerAccept()
                    data.task_manager_id = new_task.id
                    task = TaskManager_class(data)
                    task.loan_case_task_manager_set_on_work(self.db_session)
                    
            
            
            i=i+1
                    
            if i % 10000 == 0:
                
                cron_logger.info(f'Commited {i} loan_case elements')
                commit_object(self.db_session)
    
        
        commit_object(self.db_session)
        return 'OK'



class KadDistribution(DistributionManager):
    pass



class ProblemDistribution(DistributionManager):
    pass