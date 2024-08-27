from app.models.brief_case.directories.client_region import client_region
from app.models.brief_case.directories.local_code import local_code
from ..structure.region.region_crud import get_region
from app.models.structure.departments import Departments
from fastapi import HTTPException
from sqlalchemy.sql import text
from app.models.users.attached_branches import attached_branches
from app.models.statuses.attached_type_model import AttachedType
from ...common.is_empty import is_empty, is_exists
from ...common.commit import commit_object, flush_object


def attach_local_codes_to_user(request, db_session):
    lis = list()
    get_attached = db_session.query(attached_branches).filter(attached_branches.user_id == request.user_id).filter(attached_branches.attached_type_id == request.attach_type).all()
    
    if get_attached is not None:
        for role in get_attached:
            lis.append(role.local_code_id)
        if request.local_code_list is not None:
                for append in request.local_code_list:
                    if append not in lis:
                        try:
                            new_attach = attached_branches(user_id = request.user_id,
                                                           local_code_id = append,
                                                           department_id = request.department_id,
                                                           attached_type_id = request.attach_type)
                            db_session.add(new_attach)
                            flush_object(db_session)
                        except:
                            db_session.rollback()
                            get_attached = db_session.query(local_code).filter(local_code.id == append).first()
                            raise HTTPException(status_code=400, detail=f'Local Code ({get_attached.code}) already attached!')
        for remove in lis:
            if remove not in request.local_code_list:
                get_attached = db_session.query(attached_branches).filter(attached_branches.user_id == request.user_id)\
                    .filter(attached_branches.local_code_id == remove).filter(attached_branches.department_id == request.department_id)\
                        .filter(attached_branches.attached_type_id == request.attach_type).first()
                db_session.delete(get_attached)
                
    commit_object(db_session)
    return {"result":"OK"}


def get_user_attached_locals1(user_id, region_id, department_id, attach_type_id, db_session):
    
    get_attached = db_session.query(attached_branches).filter(attached_branches.user_id == user_id)\
        .filter(attached_branches.department_id == department_id)\
            .filter(attached_branches.attached_type_id == attach_type_id)
            
    if region_id is not None:
        get_attached = get_attached.join(local_code, local_code.id==attached_branches.local_code_id)\
            .join(client_region, client_region.id==local_code.region_id)\
            .filter(client_region.id == region_id)
        
    
    get_attached = get_attached.filter(attached_branches.local_code_id!=None).all()
    att_branches = []
    if get_attached !=[]:
        for dep in get_attached:
            att_branches.append({"id":dep.local_code and dep.local_code.id or None,
                        "code":dep.local_code and dep.local_code.code or None,
                        "name":dep.local_code and dep.local_code.name or None})
    return att_branches



def get_user_attached_locals(user, user_id, region_id, department_id, attach_type_id, db_session):
    get_attached = []
    if user.roles[0].level == 99:
       get_attached = get_attached_locals_for_superuser(user_id, department_id, attach_type_id, db_session)
    if user.roles[0].level == 30:
       get_attached = get_attached_locals_for_superviser(user.region_id, attach_type_id, db_session)
    if user.roles[0].level == 20:
        get_attached = get_attached_locals_for_main_admin(user.id, region_id, attach_type_id, db_session)
    elif user.roles[0].level <= 40 and user.roles[0].level > 30:
        get_attached = get_attached_locals_for_main_superviser(region_id, attach_type_id, db_session)
    
    att_branches = []
    if get_attached !=[]:
        for dep in get_attached:
            att_branches.append({"id":dep.id,
                        "code":dep.code,
                        "name":dep.name})
    return att_branches



def get_attached_locals_for_superuser(user_id, department_id, attach_type_id, db_session):
    
    return db_session.execute(text(f'''SELECT DISTINCT
                                                LC.ID,
                                                LC.CODE,
                                                LC.NAME
                                            FROM
                                                ATTACHED_REGIONS AB
                                                JOIN LOCAL_CODE LC ON AB.REGION_ID = LC.REGION_ID
                                            WHERE
                                                AB.ATTACHED_TYPE_ID = {attach_type_id}
                                                AND AB.USER_ID= {user_id}
                                                AND AB.DEPARTMENT_ID= {department_id}
                                               
                                           '''))









def get_attached_locals_for_superviser(region_id,  attach_type_id, db_session):
    region_script = ''
    if region_id is not None:
        region_script= f'AND CR.ID = {region_id}'
    
    return db_session.execute(text(f'''SELECT DISTINCT
                                                LC.ID,
                                                LC.CODE,
                                                LC.NAME
                                            FROM
                                                CLIENT_REGION CR
                                                JOIN LOCAL_CODE LC ON LC.REGION_ID = CR.ID
                                                JOIN ATTACHED_REGIONS AB ON AB.REGION_ID = LC.REGION_ID
                                            WHERE
                                                AB.ATTACHED_TYPE_ID = {attach_type_id}
                                               {region_script}
                                               
                                           '''))



def get_attached_locals_for_main_admin(user_id, region_id,  attach_type_id, db_session):
    print(user_id, region_id,  attach_type_id)
    region_script = ''
    if region_id is not None:
        region_script= f'AND CR.ID = {region_id}'
    
    return db_session.execute(text(f'''SELECT DISTINCT
                                                LC.ID,
                                                LC.CODE,
                                                LC.NAME
                                            FROM
                                                CLIENT_REGION CR
                                                JOIN LOCAL_CODE LC ON LC.REGION_ID = CR.ID
                                                JOIN ATTACHED_REGIONS AB ON AB.REGION_ID = CR.ID
                                            WHERE
                                                AB.ATTACHED_TYPE_ID = {attach_type_id}
                                               {region_script}
                                               AND AB.USER_ID = {user_id}
                                           '''))





def get_attached_locals_for_main_superviser(region_id,  attach_type_id, db_session):
    region_script = ''
    if region_id is not None:
        region_script= f'AND CR.ID = {region_id}'
    
    return db_session.execute(text(f'''SELECT DISTINCT
                                                LC.ID,
                                                LC.CODE,
                                                LC.NAME
                                            FROM
                                                CLIENT_REGION CR
                                                JOIN LOCAL_CODE LC ON LC.REGION_ID = CR.ID
                                                JOIN ATTACHED_BRANCHES AB ON AB.LOCAL_CODE_ID = LC.ID
                                            WHERE
                                                AB.ATTACHED_TYPE_ID = {attach_type_id}
                                               {region_script}
                                           '''))



def get_attached_types(db_session):
    get_attached_types = db_session.query(AttachedType).all()
    att_types = []
    if get_attached_types !=[]:
        for types in get_attached_types:
            att_types.append({"id":types.id,
                        "code":types.code,
                        "name":types.name})
    return att_types



def get_attached_locals_users(user, department, main_responsible, attached_type, local_code_id, db_session):
    get_attached = None
    if user.roles[0].level == 30:
       get_attached = get_attached_user_for_superviser(user, department, attached_type, local_code_id, db_session)
    elif user.roles[0].level == 20:
        get_attached = get_attached_users_for_main_admin(user.id, department, attached_type, local_code_id, db_session)
    elif user.roles[0].level <= 40 and user.roles[0].level > 30:
        get_attached = get_second_users_for_main_superviser(main_responsible, attached_type, local_code_id, db_session)
    attached_users=[]
    if get_attached is not None:
        for attached in get_attached:
            attached_users.append({'id':attached.id,
                                'full_name':attached.full_name})
    return attached_users

def get_attached_users_for_main_superviser(user, department, attached_type, local_code_id, db_session):
    get_attached = None
    if user.roles[0].level <= 40 and user.roles[0].level > 30:
        get_attached = get_attached_user_for_main_superviser(department, attached_type, local_code_id, db_session)
    attached_users=[]
    if get_attached is not None:
        for attached in get_attached:
            attached_users.append({'id':attached.id,
                                'full_name':attached.full_name})
    return attached_users





def get_attached_users_for_main_admin(user_id, department, attached_type, local_code_id, db_session):
    local_script = ''
    if local_code_id is not None:
        local_script= f'AND LC.ID = {local_code_id}'
    
    return db_session.execute(text(f'''SELECT U.ID, U.FULL_NAME
                                                FROM USERS U
                                                LEFT JOIN user_role UR ON UR.user_id=U.ID
                                                LEFT JOIN roles R ON R.id = UR.role_id 
                                                WHERE U.LOCAL_CODE IN
                                                (SELECT LC.ID
                                                FROM LOCAL_CODE LC
                                                JOIN ATTACHED_BRANCHES AB ON LC.ID = AB.LOCAL_CODE_ID
                                                WHERE 
                                                AB.USER_ID = {user_id}
                                                AND AB.DEPARTMENT_ID = {department}
                                                AND AB.ATTACHED_TYPE_ID = {attached_type}
                                                {local_script}
                                                )
                                                AND U.DEPARTMENT = {department}
                                                AND R.LEVEL <=20 GROUP BY U.ID, U.full_name
                                           '''))
    
    
    
def get_attached_user_for_superviser(user, department, attached_type, local_code_id, db_session):
    
    local_script = ''
    if local_code_id is not None:
        local_script= f'AND AB.LOCAL_CODE_ID = {local_code_id}'
    
    return db_session.execute(text(f'''SELECT U.ID, U.FULL_NAME
                                                FROM USERS U
                                                LEFT JOIN user_role UR ON UR.user_id=U.ID
                                                LEFT JOIN roles R ON R.id = UR.role_id 
                                                WHERE U.LOCAL_CODE IN
                                                (SELECT LC.ID
                                                FROM LOCAL_CODE LC
                                                JOIN ATTACHED_BRANCHES AB ON LC.ID = AB.LOCAL_CODE_ID
                                                WHERE 
                                                 AB.DEPARTMENT_ID = {department}
                                                AND AB.ATTACHED_TYPE_ID = {attached_type}
                                               {local_script})
                                                --AND U.ID != {user.id}
                                                AND U.DEPARTMENT = {department}
                                                AND U.REGION_ID = {user.region_id}
                                                AND R.LEVEL <=20 GROUP BY U.ID, U.full_name
                                           '''))
    
    
    
def get_attached_user_for_main_superviser(department, attached_type, local_code_id, db_session):
    
    local_script = ''
    if local_code_id is not None:
        local_script= f'AND AB.LOCAL_CODE_ID = {local_code_id}'
        
    return db_session.execute(text(f'''SELECT DISTINCT
                                            AB.USER_ID AS ID,
                                            U.FULL_NAME
                                        FROM
                                            USERS U
                                            JOIN ATTACHED_BRANCHES AB ON AB.USER_ID = U.ID
                                        WHERE
                                            AB.ATTACHED_TYPE_ID = {attached_type}
                                            --AB.DEPARTMENT_ID = {department}
                                            {local_script}
                                           '''))
    
    


def get_second_users_for_main_superviser(main_responsible, attached_type, local_code_id, db_session):
    local_script = ''
    if local_code_id is not None:
        local_script= f'AND LC.ID = {local_code_id}'
    user_id = ''
    main_resp = ''
    if main_responsible is not None:
        user_id = f'AB.USER_ID = {main_responsible} AND'
        main_resp = f'AND U.DEPARTMENT = (select department from users where id={main_responsible})'
        
    return db_session.execute(text(f'''SELECT U.ID, U.FULL_NAME
                                                FROM USERS U
                                                LEFT JOIN user_role UR ON UR.user_id=U.ID
                                                LEFT JOIN roles R ON R.id = UR.role_id 
                                                WHERE U.LOCAL_CODE IN
                                                (SELECT LC.ID
                                                FROM LOCAL_CODE LC
                                                JOIN ATTACHED_BRANCHES AB ON LC.ID = AB.LOCAL_CODE_ID
                                                WHERE 
                                                {user_id}
                                                
                                                AB.ATTACHED_TYPE_ID = {attached_type}
                                                {local_script}
                                                )
                                                {main_resp}
                                                AND R.LEVEL <=10 GROUP BY U.ID, U.full_name
                                           '''))