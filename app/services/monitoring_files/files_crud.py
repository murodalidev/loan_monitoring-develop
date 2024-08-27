import datetime
from fastapi import HTTPException
from sqlalchemy import or_
from app.models.files.monitoring_files_model import MonitoringFiles
from app.models.files.file_types import FTypes
from app.models.files.files_types import FilesTypes
from app.models.juridical_case.juridical_case_model import JuridicalCase
from app.models.users.users import Users
from fastapi import BackgroundTasks
from ...common.commit import commit_object, flush_object
from  app.services.loan_monitoring.problems_case import letters_crud
from  app.services.users.users_crud import Users as users



def get_files_by_param(juridical_case_id, db_session):
    get_juridical_case = db_session.query(JuridicalCase).filter(JuridicalCase.id == juridical_case_id).first()
    files_id = [juridica_file.id for juridica_file in get_juridical_case.files]  
    category= []
    categories = []
    get_files = db_session.query(MonitoringFiles).filter(MonitoringFiles.id.in_(files_id)).all()
    for value in get_files:
        if value.general_task_id not in category:
            category.append(value.general_task_id)
    files = []
    for cat in category:
        for file in get_files:
            if cat == file.general_task_id:
                files.append({"id":file.id,
                              "created_at":file.created_at,
                             "file_url":file.file_url,
                             "is_changed":file.is_changed,
                             "type":{"id":file.type.id,
                                     "name":file.type.name,
                                     "type": file.type.code},
                             "updated_at":file.updated_at and file.updated_at or None})
        categories.append({"general_task_id":cat,
                           "files":files})
        files = []
    
    return categories



def get_case_files(case):
    files = []
    for file in case.files:
            files.append({"id":file.id,
                            "created_at":file.created_at,
                            "file_url":file.file_url,
                            "is_correct":file.is_correct,
                            "is_changed":file.is_changed,
                            "type":{"id":file.type.id,
                                    "name":file.type.name,
                                    "type": file.type.code,
                                    "is_required":file.type.is_required},
                            "updated_at":file.updated_at})
    
    
    
    return files





def get_file_types(db_session):
    ftypes = []
    get_types = db_session.query(FTypes).all()
    for ftype in get_types:
            ftypes.append({"id":ftype.id,
                                    "name":ftype.name,
                                    "type": ftype.code})
    
    
    
    return ftypes




def set_wrong_files(files_id, target, db_session):
    set_files_is_changed_false(target, db_session)
    get_files = db_session.query(MonitoringFiles).filter(MonitoringFiles.id.in_(files_id)).all()
    file_path = []
    for file in get_files:
        file.is_correct = False
        flush_object(db_session)
        file_path.append(file.file_url)
    return file_path
    
def set_files_is_changed_false(target, db_session):
    
    f_list = [file.id for file in target.files]
    get_files = db_session.query(MonitoringFiles).filter(MonitoringFiles.id.in_(f_list)).all()
    for file in get_files:
        file.is_changed = False
        flush_object(db_session)
    


def append_file_to_types(request, db_session):
    lis = list()
    get_file_types = db_session.query(FilesTypes).filter(FilesTypes.general_tasks_id == request.general_task_id).all()
    
    if get_file_types is not None:
        for ftype in get_file_types:
            lis.append(ftype.f_types_id)
        if request.type_list is not None:
                for append in request.type_list:
                    
                    if append not in lis:
                        try:
                            new_attach = FilesTypes(general_tasks_id = request.general_task_id,
                                                    f_types_id = append)
                            db_session.add(new_attach)
                            flush_object(db_session)
                        except:
                            db_session.rollback()
                            raise HTTPException(status_code=400, detail=f'Type ({append}) already attached!')
        
        for remove in lis:
            if remove not in request.type_list:
                get_attached = db_session.query(FilesTypes).filter(FilesTypes.general_tasks_id == request.general_task_id)\
                    .filter(FilesTypes.f_types_id == remove).first()
                db_session.delete(get_attached)
    commit_object(db_session)
    return {"result":"OK"}




def get_ftypes_by_general_task(general_task_id, db_session):
    get_types = db_session.query(FilesTypes).filter(FilesTypes.general_tasks_id == general_task_id).all()
    ftypes = []
    
    for ftype in get_types:
            ftypes.append({"id":ftype.type.id,
                                    "name":ftype.type.name,
                                    "type": ftype.type.code,
                                    "is_required": ftype.type.is_required,
                                    "is_multiple": ftype.type.is_multiple})
    
    return ftypes
        