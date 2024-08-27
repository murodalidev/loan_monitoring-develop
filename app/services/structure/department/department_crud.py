from app.models.brief_case.directories.client_region import client_region
from ..region.region_crud import get_region
from app.models.structure.departments import Departments
from ....common.is_empty import is_empty, is_exists
from ....common.commit import commit_object


def create_department(request, db_session):
    get_dep = db_session.query(Departments).filter(Departments.name == request.department_name)\
        .filter(client_region.id == request.region_id).first()
    is_empty(get_dep, 400, 'department has already created!')
    new_department = Departments(name=request.department_name, region_id=request.region_id)
    db_session.add(new_department)
    commit_object(db_session)
    return {"result":"OK"}



def get_all_departments(db_session):
    get_deps = db_session.query(Departments).all()
    departments = []
    for dep in get_deps:
        departments.append({"id":dep.id,
               "department_name":dep.name,
               "region":dep.region})
    return departments







def get_department(department, db_session):
    return db_session.query(Departments).filter(Departments.id == department).first()



def update_department(id, request, db_session):
    get_dep = db_session.query(Departments).filter(Departments.id == id).first()
    is_empty(get_dep, 400, 'department has already created!')
    if request.department_name is not None:
        get_dep.name=request.department_name
    if request.region_id is not None:
        get_dep.region_id= request.region_id
    commit_object(db_session)
    return {"result":"OK"}



def delete_department(id, db_session):
    get_dep = db_session.query(Departments).filter(Departments.id == id).first()
    is_exists(get_dep, 400, 'Departments not found')
    db_session.delete(get_dep)
    commit_object(db_session)
    return {"result":"OK"}

