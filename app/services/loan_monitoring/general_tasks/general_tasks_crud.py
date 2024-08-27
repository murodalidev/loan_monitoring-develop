from ....models.monitoring_task_manager.general_tasks_model import GeneralTasks
from ....common.dictionaries.departments_dictionary import DEP
from ....common.dictionaries.general_tasks_dictionary import GTCAT


def get_general_tasks_by_category_id(category_id, db_session):
    general_tasks_list = []
    get_tasks = db_session.query(GeneralTasks).filter(GeneralTasks.category_id == category_id).order_by(GeneralTasks.id.asc()).all()
    
    for tasks in get_tasks:
        general_tasks_list.append({"id":tasks.id,
                                   "name":tasks.name,
                                   "category":tasks.category,
                                   "level":tasks.level})
        
    return general_tasks_list



def get_general_tasks_for_filter(department, db_session):
    if department == DEP.PROBLEM.value:
        id_list = (GTCAT.PROBLEM.value, GTCAT.PROBLEMS_ARRIVAL.value)
        tasks = get_general_tasks(id_list, db_session)
    elif department == DEP.JURIDIC.value:
        id_list = (GTCAT.JURIDIC.value, GTCAT.JURIDIC_PUNISH.value)
        tasks = get_general_tasks(id_list, db_session)
    else:
        id_list = [GTCAT.MONIT.value]
        tasks = get_general_tasks(id_list, db_session)
    
    return tasks



def get_general_tasks(id_list, db_session):
    general_tasks_list = []
    get_tasks = db_session.query(GeneralTasks).filter(GeneralTasks.category_id.in_(id_list)).order_by(GeneralTasks.id.asc()).all()
    
    for tasks in get_tasks:
        general_tasks_list.append({"id":tasks.id,
                                   "name":tasks.name,
                                   "category":tasks.category,
                                   "level":tasks.level})
        
    return general_tasks_list
