import datetime
from ....models.monitoring_task_manager.task_manager_model import TaskManager
from ....models.monitoring_task_manager.general_tasks_model import GeneralTasks
from ....models.statuses.task_status_model import TaskStatus
from ....models.statuses.montoring_status_model import MonitoringStatus
from ....common.commit import flush_object
from ....common.dictionaries.task_status_dictionaries import task_status
from ....common.dictionaries.departments_dictionary import DEP
from ....common.dictionaries.general_tasks_dictionary import JGT, MGT, PGT, GTCAT, KGT
class TaskManager_class():
    def __init__(self, data=None):
        self.__data = data


    def get_task_managers_by_id(case_tasks, db_session):
        task = {}
        
        task_manager = db_session.query(TaskManager).filter(TaskManager.id == case_tasks.id).first()
        
        task = {"id":task_manager.id,
                "deadline":task_manager.deadline,
                "status":task_manager.status,
                "created_at":task_manager.created_at,
                "updated_at":task_manager.updated_at,
                "general_task":{"id":task_manager.general_task.id,
                                "name":task_manager.general_task.name,
                                "category":task_manager.general_task.category,
                                "level":task_manager.general_task.level}}
        
        return task


    
    def get_task_manager_by_id(case_task, db_session):
        tasks = {}
        
        task_manager = db_session.query(TaskManager).filter(TaskManager.id == case_task.id).first()
        
        tasks = {"id":task_manager.id,
                "deadline":task_manager.deadline,
                "status":task_manager.status,
                "created_at":task_manager.created_at,
                "updated_at":task_manager.updated_at,
                "general_task":{"id":task_manager.general_task.id,
                                "name":task_manager.general_task.name,
                                "category":task_manager.general_task.category,
                                "level":task_manager.general_task.level}}
        
        return tasks




    def create_task_manager_when_user_accept_loan(self, db_session):#used
        general_task = self._get_general_task_by_category(MGT.NEW.value,GTCAT.MONIT.value,db_session)
        new_task = TaskManager(general_task_id = general_task.id,
                                task_status_id = task_status['начато'],
                                created_at = datetime.datetime.now()
                                )
        db_session.add(new_task)
        return new_task
    
    
    def create_task_manager_when_business_user_accept_loan(self, db_session):#used
        general_task = self._get_general_task_by_category(MGT.NEW.value,GTCAT.MONIT.value,db_session) # TODO:когда появятся бизнеса для кад заменить GTCAT MONIT -> BUSINESS
        new_task = TaskManager(general_task_id = general_task.id,
                                task_status_id = task_status['начато'],
                                created_at = datetime.datetime.now()
                                )
        db_session.add(new_task)
        return new_task
    
    
    def create_task_manager_when_kad_user_accept_loan(self, db_session):#used
        general_task = self._get_general_task_by_category(KGT.SEND_1_LETTER.value, GTCAT.KAD.value,db_session)
        new_task = TaskManager(general_task_id = general_task.id,
                                task_status_id = task_status['начато'],
                                created_at = datetime.datetime.now()
                                )
        db_session.add(new_task)
        return new_task
    
    
    def create_task_manager_appointed_target(self, db_session):#used
        general_task = self._get_general_task_by_category(MGT.TARGET_MONITORING.value,GTCAT.MONIT.value,db_session)
        new_task = TaskManager(general_task_id = general_task.id,
                                task_status_id = task_status['завершено'],
                                created_at = datetime.datetime.now()
                                )
        db_session.add(new_task)
        return new_task
    
    
        
    def create_task_manager_when_user_accept_problems(self, db_session):#used
        general_task = self._get_general_task_by_category(PGT.NEW.value,GTCAT.PROBLEM.value,db_session)
        new_task = TaskManager(general_task_id = general_task.id,
                                task_status_id = task_status['начато'],
                                created_at = datetime.datetime.now()
                                )
        db_session.add(new_task)
        return new_task
    
    def create_task_manager_when_user_accept_juridical(self, db_session):#used
        general_task = self._get_general_task_by_category(JGT.APPOINT_RESPONSIBLE.value,GTCAT.JURIDIC.value,db_session)
        new_task = TaskManager(general_task_id = general_task.id,
                                task_status_id = task_status['начато'],
                                created_at = datetime.datetime.now()
                                )
        db_session.add(new_task)
        return new_task
    
    def create_task_manager_when_set_target_monitoring(self, db_session):#used
        new_task = TaskManager(general_task_id = self.__data.general_task_id,
                                task_status_id = task_status['начато'],
                                created_at = datetime.datetime.now()
                                )
        db_session.add(new_task)
        flush_object(db_session)
        return new_task
    
    
    
    
    
    def create_task_manager_when_set_scheduled_monitoring(self, db_session):#used
        new_task = TaskManager(general_task_id = self.__data.general_task_id,
                                task_status_id = task_status['начато'],
                                created_at = datetime.datetime.now(),
                                )
        db_session.add(new_task)
        flush_object(db_session)
        return new_task
    
    
    def create_task_manager_when_set_problems_letter(self, db_session):#used
        new_task = TaskManager(general_task_id = self.__data.general_task_id,
                                task_status_id = task_status['начато'],
                                created_at = datetime.datetime.now()
                                )
        db_session.add(new_task)
        flush_object(db_session)
        return new_task
    
    
    def create_task_manager_when_set_juridical_intended_task(self, db_session):#used
        
        new_task = TaskManager(general_task_id = self.__data.general_task_id,
                                task_status_id = task_status['начато'],
                                created_at = datetime.datetime.now(),
                                deadline = self.__data.deadline
                                )
        db_session.add(new_task)
        flush_object(db_session)
        return new_task
    
    
    
    
    
    def loan_case_task_manager_set_on_work(self, db_session):#used
        general_task = self._get_general_task_by_category(MGT.ON_WORK.value,GTCAT.MONIT.value,db_session)
        get_task_manager = db_session.query(TaskManager).filter(TaskManager.id == self.__data.task_manager_id).first()
        get_task_manager.general_task_id = general_task.id
        get_task_manager.task_status_id = task_status['завершено']
        flush_object(db_session)
        return get_task_manager
    
        
    def _get_general_task_by_category(self, id, category_id, db_session):
        return db_session.query(GeneralTasks).filter(GeneralTasks.category_id == category_id).filter(GeneralTasks.id == id).first()
        
    
    # def _get_task_status_by_name(self, name, db_session):
    #     return db_session.query(TaskStatus).filter(TaskStatus.name == name).first()
    
    
    
    
    def update_task_manager(self, db_session):#used
        get_task_manager = db_session.query(TaskManager).filter(TaskManager.id == self.__data.task_manager_id).first()
        if hasattr(self.__data, 'general_task_id') and self.__data.general_task_id is not None: 
            get_task_manager.general_task_id = self.__data.general_task_id
        if hasattr(self.__data, 'task_status') and self.__data.task_status is not None:
            get_task_manager.task_status_id = self.__data.task_status
        get_task_manager.updated_at = datetime.datetime.now()
        flush_object(db_session)
        return get_task_manager
    
    
    
    
    def update_task_manager_problems_set_closed(self, db_session):#used
        get_task_manager = db_session.query(TaskManager).filter(TaskManager.id == self.__data.task_manager_id).first()
        get_task_manager.updated_at = datetime.datetime.now()
        get_task_manager.general_task_id = PGT.REPAID.value
        flush_object(db_session)
        return get_task_manager
    
    def update_task_manager_monitoring_set_in_work(self, db_session):#used
        get_task_manager = db_session.query(TaskManager).filter(TaskManager.id == self.__data.task_manager_id).first()
        get_task_manager.updated_at = datetime.datetime.now()
        get_task_manager.general_task_id = MGT.ON_WORK
        flush_object(db_session)
        return get_task_manager
    
    
    
    def get_task_by_id(self, db_session):#used
        return db_session.query(TaskManager).filter(TaskManager.id == self.__data.task_manager_id).first()
    
    
    def get_task_by_general_task_id(self, db_session):#used
        return db_session.query(TaskManager).filter(TaskManager.general_task_id == self.__data.general_task_id).first()
    
    
    

def get_task_status(db_session):
    task_statuses = []
        
    get_task_status = db_session.query(MonitoringStatus).all()
    
    for status in get_task_status:
    
        task_statuses.append({"id":status.id,
                "name":status.name,
                "code":status.code,
                })
    
    return task_statuses