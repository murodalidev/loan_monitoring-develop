from fastapi import HTTPException
from app.models.rbac.permission import permission
from app.models.rbac.permission_category import permission_category
from app.models.rbac.roles import roles
from ...services.rbac import roles as roles_crud
from ...common.commit import commit_object
from ...common.is_empty import is_empty, is_exists, warning


def update_endpoints(routes, db_session):
    permission_categories = db_session.query(permission_category).all()
    endpoints_check_add_or_remove(permission_categories, routes, db_session)
    permissions = db_session.query(permission).all()
    permissions_check_add_or_remove(permissions, routes, db_session)
    
    for path in routes:
        get_endpoint_category = db_session.query(permission_category).filter(permission_category.name == path['tag']).first()
        if get_endpoint_category is not None:
            get_endpoint_category.name = path['tag']
            commit_object(db_session)
            
            
            for url in  path['path']:
                permiss = db_session.query(permission).filter(permission.route == url).first()
                if permiss is None:
                    new_permiss = permission(route = url, category_id = get_endpoint_category.id)
                    db_session.add(new_permiss)
                    commit_object(db_session)
        else:
            new_endpoint_category = permission_category(name = path['tag'])
            db_session.add(new_endpoint_category)
            commit_object(db_session)
            
            for url in  path['path']:
                permiss = db_session.query(permission).filter(permission.route == url).first()
                if permiss is None:
                    new_permiss = permission(route = url, category_id = new_endpoint_category.id)
                    db_session.add(new_permiss)
                    commit_object(db_session)
    return {"result":"OK"}

def endpoints_check_add_or_remove(endpoint_categories, routes, db_session):
    temp=0
    for endpoint_category in endpoint_categories:
        for path in routes:
            if path['tag'] == endpoint_category.name:
                temp=1
        if temp == 0:
            premissions = db_session.query(permission).filter(permission.category_id == endpoint_category.id).all()
            for permiss in premissions:
                permiss.category_id = None
                commit_object(db_session)
                
            endpoint_category1 = db_session.query(permission_category).filter(permission_category.id == endpoint_category.id).first()
            db_session.delete(endpoint_category1)
            commit_object(db_session)
        temp=0
    pass

def permissions_check_add_or_remove(permissions, routes, db_session):
    temp=0
    for permiss in permissions:
        for path in routes:
            for pathes in path['path']:
                if pathes == permiss.route:
                    temp=1
        if temp == 0:
            for role in permiss.permission:
                print(role.name, " -- ",permiss.id)
                # role.role_permission.remove(permiss)
            permissions1 = db_session.query(permission).filter(permission.id == permiss.id).first()
            db_session.delete(permissions1)
            commit_object(db_session)
        temp=0
    pass






def get_all_path_tags(db_session):
    data=[]
    categories = db_session.query(permission_category).all()
    for category in categories:
        data.append({'id': category.id,
                     "category": category.name,
                     "paths": category.endpoint})

    return data


def set_name_for_paths(request, db_session):
    for name in request.names:
        permiss = db_session.query(permission).filter(permission.id == name.permission_id).first()
        if name is not None:
            permiss.name = name.name
        db_session.add(permiss) 
        commit_object(db_session)
    return {"result":"OK"}


def append_or_remove_permission(request, db_session):
    user_role = db_session.query(roles).filter(roles.id == request.role_id).first()
    l = list()
    if user_role is not None:
        for role in user_role.role_permission:
            l.append(role.id)
    if request.append is not None:
        
            for append in request.append:
                if append.permission_id not in l:
                    try:
                        permiss = db_session.query(permission).filter(permission.id == append.permission_id).first()
                    except:
                        db_session.rollback()
                        raise HTTPException(status_code=400, detail='Permission doesn`t exist')
                    
                    user_role.role_permission.append(permiss)
                db_session.add(user_role)
        
        
    if request.remove is not None:
        
        user_role = db_session.query(roles).filter(roles.id == request.role_id).first()
        for append in request.remove:
            if append.permission_id in l:
                try:
                    permiss = db_session.query(permission).filter(permission.id == append.permission_id).first()
                except:
                    db_session.rollback()
                    raise HTTPException(status_code=400, detail='Permission doesn`t exist')
                
                user_role.role_permission.remove(permiss)
            db_session.add(user_role)
    commit_object(db_session)
    return{"result":"OK"}


def append_all_permissions_to_role(db_session):
    role = db_session.query(roles).filter(roles.id == 1).first()
    permiss = db_session.query(permission).all()
    
    for perm in permiss:
        role.role_permission.append(perm)
        db_session.add(role)
    commit_object(db_session)
    return 0

def delete_role_permissions(role_id, db_session):
    role = db_session.query(roles).filter(roles.id == role_id).first()
    if role is not None:
        if role.role_permission:
            role.role_permission.clear()
            db_session.add(role)
    commit_object(db_session)
    return {"result":"OK"}


def get_role_permissions(role_id, db_session):
    role = db_session.query(roles).filter(roles.id == role_id).first()
    permissions = []
    for permiss in role.role_permission:
        permissions.append({"id": permiss.id,
                            "name": permiss.name,
                            "endpoint": permiss.route})
    
    return {"role": role.id,
            "role_name": role.name,
            "permissions": permissions}
    


def get_user_permissions(user_id, db_session):
    permissions = []
    user_roles = roles_crud.get_user_roles_id_by_array(user_id, db_session)
    for role in user_roles:
        permissions.extend(get_role_permissions(role, db_session)["permissions"])
    return permissions

