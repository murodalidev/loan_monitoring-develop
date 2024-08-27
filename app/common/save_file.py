import uuid
import shutil
import os
import datetime
from app.db.connect_db import SessionManager
from app.models.files.file_types import FTypes
from ..common.commit import commit_object, flush_object
from ..models.files.monitoring_files_model import MonitoringFiles

def get_file_types():
    with SessionManager() as db_session:
        get_file_types = db_session.query(FTypes.code, FTypes.id).all()
        file_types = {}
        for file_type, code in get_file_types:
            file_types[file_type] = code
        return file_types



def save_multiple_files(directory, **kwargs):
    file_types = get_file_types()
    file_paths = []
    for file in kwargs:
        return_file_dict(directory, kwargs.get(file), file_types[file], file, file_paths)
    
    return file_paths



def return_file_dict(directory, file, file_type_code, file_type_name, file_paths):
    if isinstance(file, list) and file !=[]:
        for fil in file:
            file_paths.append({"type_code": file_type_code,
                               "file_type_name": file_type_name,
                           "name": save_file(directory, fil)})
    else:    
        if file:
            file_paths.append({"type_code": file_type_code,
                           "name": save_file(directory, file)})
    return file_paths



def save_file(directory, file):
    
    root_directory = f"project_files/{directory}"
    
    isExist = os.path.exists(root_directory)
    if not isExist:
        os.makedirs(root_directory)
        
    if file:
        out_file_path = f"{root_directory}/{str(uuid.uuid4())[:8]+'-'+file.filename}"
        with open(out_file_path,'wb') as out_file:
            shutil.copyfileobj(file.file, out_file)
    else:
        out_file_path = None
    return out_file_path




def  append_monitoring_files(monitoring, file_path, db_session, addition=None):
    f_list = []
    is_changed = False
    is_files_exist = False
    if monitoring.files != []:
        f_list = [{"id":file.id,"type":file.ftype,"url": file.file_url, "is_correct": file.is_correct} for file in monitoring.files]
        is_files_exist = True
    for fil in f_list:
        
        if fil['is_correct'] == False:
            is_changed = True
            os.remove(fil['url'])
            get_file = db_session.query(MonitoringFiles).filter(MonitoringFiles.id==fil["id"]).first()
            monitoring.files.remove(get_file)
            db_session.add(monitoring)
            db_session.delete(get_file)
            commit_object(db_session)
    if is_files_exist and  not is_changed and addition is None:
        return 0
    else:
        for file in file_path:
            new_file = MonitoringFiles(file_url = file['name'],
                                        ftype = file['type_code'],
                                        is_changed = is_changed,
                                        created_at = datetime.datetime.now())
            db_session.add(new_file)
            flush_object(db_session)
            monitoring.files.append(new_file)
            db_session.add(monitoring)


def attach_non_target_files(monitoring, file_path, db_session):
    for file in file_path:
        monitoring.files.append(file)
        db_session.add(monitoring)





