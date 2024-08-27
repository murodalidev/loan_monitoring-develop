from ....models.monitoring_task_manager.general_tasks_category_model import GeneralTasksCategory
from ....common.is_empty import is_empty, is_exists
from ....common.commit import commit_object


def get_all(db_session):
    general_tasks_category_list = []
    get_category = db_session.query(GeneralTasksCategory).all()
    
    for category in get_category:
        general_tasks_category_list.append({"id":category.id,
                                   "name":category.name})
        
    return general_tasks_category_list

def create_general_tasks_category(request, db_session):
    get_category = db_session.query(GeneralTasksCategory).filter(GeneralTasksCategory.name == request.name).first()
    is_empty(get_category, 400, 'category has already created!')

    new_general_task_category = GeneralTasksCategory(name = request.name)

    db_session.add(new_general_task_category)
    commit_object(db_session)

    return {"status": "OK"}

def update_general_tasks_category(id, request, db_session):
    check_category = db_session.query(GeneralTasksCategory).filter(GeneralTasksCategory.name == request.name).filter(GeneralTasksCategory.id == id).first()
    is_empty(check_category, 400, 'General task category has already created')

    get_general_task = db_session.query(GeneralTasksCategory).filter(GeneralTasksCategory.id == id).first()
    get_general_task.name = request.name

    commit_object(db_session)

    return {"result":"OK"}



def delete_general_tasks_category(id, db_session):
    get_general_task_category = db_session.query(GeneralTasksCategory).filter(GeneralTasksCategory.id == id).first()
    is_exists(get_general_task_category, 400, 'General task category not found')

    db_session.delete(get_general_task_category)
    commit_object(db_session)
    
    return {"result":"OK"}