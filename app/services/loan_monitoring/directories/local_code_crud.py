from openpyxl import load_workbook
import time
from ....models.brief_case.directories.bank_mfo import bank_mfo
from ....models.brief_case.directories.client_region import client_region
from ....models.brief_case.directories.local_code import local_code, local_code_edit
from ....common.is_empty import is_empty, is_exists
from ....common.commit import commit_object
import datetime
from sqlalchemy import func



def create_local_code(request, db_session):
    get_local = db_session.query(local_code).filter(local_code.code == request.code).first()
    is_empty(get_local, 400, 'local code has already created!')
    
    new_local_code = local_code(name=request.name,
                                    code=request.code,
                                    region_id=request.region_id,
                                    head=request.head,
                                    index = request.index, 
                                    address = request.address,                                      
                                    inn = request.inn, 
                                    phone_number = request.phone_number, 
                                    manager = request.manager,
                                    created_at = datetime.datetime.now())
    db_session.add(new_local_code)
    commit_object(db_session)
    return {"result":"OK"}




def get_local_codes_by_param(size, page, region_id, local_code_id, name, db_session):
    get_locals = db_session.query(local_code)
    
    if region_id is not None:
        get_locals = get_locals.filter(local_code.region_id == region_id)
    
    if local_code_id is not None:
        get_locals = get_locals.filter(local_code.id == local_code_id)
    
    if name is not None:
        get_locals = get_locals.filter(func.lower(local_code.name).like(f'%{name.lower()}%'))
        
    count = get_locals.count()
    get_locals = get_locals.limit(size).offset((page-1)*size).all()
    local_codes = []
    for local in get_locals:
        local_codes.append({"id":local.id,
                            "code":local.code,
                            "name":local.name and local.name or None,
                            "head": local.head and {"id":local.heads.id,
                                                    "name":local.heads.code+"-"+local.heads.name},
                            "region":local.region_id and local.region or None,
                            "index":local.index and local.index or None,
                            "address":local.address and local.address or None,
                            "inn":local.inn and local.inn or None,
                            "phone_number":local.phone_number and local.phone_number or None,
                            "manager":local.manager and local.manager or None})
        
    return {"items":local_codes,
            "total":count,
            "page":page,
            "size":size}



def get_local_codes_for_filter(region_id, db_session):
    get_locals = db_session.query(local_code)
    
    if region_id is not None:
        get_locals = get_locals.filter(local_code.region_id == region_id)
    
        
    get_locals = get_locals.all()
    local_codes = []
    for local in get_locals:
        local_codes.append({"id":local.id,
                            "code":local.code,
                            "name":local.name and local.name or None})
        
    return local_codes





def get_all_local_codes(db_session,region_id=None):
    get_locals = db_session.query(local_code)
    
    if region_id is not None:
        get_locals = get_locals.filter(local_code.region_id == region_id)
        
    get_locals = get_locals.all()
    
    local_codes = []
    for local in get_locals:
        local_codes.append({"id":local.id,
                            "code":local.code,
                            "name":local.name and local.name or None})
        
    return local_codes



def update_local_code(id, request, db_session):
    get_local_code = db_session.query(local_code).filter(local_code.id == id).first()
    
    code = None
    name = None
    region = None
    
    if request.code is not None:
        code = get_local_code.code
        get_local_code.code = request.code
    if request.name is not None:
        name = get_local_code.name
        get_local_code.name = request.name
    if request.region_id is not None:
        region = get_local_code.region_id
        get_local_code.region_id = request.region_id
    if request.head is not None:
        get_local_code.head = request.head
    if request.index is not None:
        get_local_code.index = request.index
    if request.address is not None:
        get_local_code.address = request.address
    if request.inn is not None:
        get_local_code.inn = request.inn
    if request.phone_number is not None:
        get_local_code.phone_number=  request.phone_number
    if request.manager is not None:
        get_local_code.manager=  request.manager
    get_local_code.updated_at = datetime.datetime.now()
    
    if code or name or region is not None:
        new_edit_local = local_code_edit(
            code_old = code,
            code_new =  request.code,
            name_old = name,
            name_new = request.name,
            region_old = region,
            region_new = request.region_id,
            created_at = datetime.datetime.now()
        )
    
    db_session.add(new_edit_local)
    commit_object(db_session)
    return {"result":"OK"}



def delete_local_code(id, db_session):
    db_session.query(local_code).filter(local_code.id == id).delete()
    commit_object(db_session)
    return {"result":"OK"}