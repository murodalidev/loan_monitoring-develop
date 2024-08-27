
from app.models.users.users import Users
from app.models.rbac.roles import roles
from app.models.rbac.permission import permission
from app.models.rbac.permission_category import permission_category
from ...common.commit import commit_object
from ...common.is_empty import is_empty, is_exists, warning



def get_all_user_roles(db_session):
    role = []
    user_roles = db_session.query(roles).all()
    for rol in user_roles:
        role.append({"id": rol.id,
                      "name": rol.name,
                      "level": rol.level})
    return role


def create_user_role(request, db_session):
    get_role = db_session.query(roles).filter(roles.name == request.name).first()
    is_empty(get_role, 400, 'User role has taken')
    
    new_role = roles(name = request.name, level = request.level)
    db_session.add(new_role)
    commit_object(db_session)
    
    return {"result":"OK"}

def update_user_role(id, request, db_session):
    validate_position = db_session.query(roles).filter(roles.name == request.name)\
        .filter(roles.id == id).first()
    is_empty(validate_position, 400 , 'User role has already exists')
    
    get_pos = db_session.query(roles).filter(roles.id == id).first()
    if request.name:
        get_pos.name = request.name
    if request.level:
        get_pos.level = request.level
    commit_object(db_session)
    return {"result":"OK"}

def delete_user_role(id, db_session):
    get_pos = db_session.query(roles).filter(roles.id == id).first()
    is_exists(get_pos, 400 , 'User role not found!')
    db_session.delete(get_pos)
    commit_object(db_session)
    return {"result":"OK"}



def get_all_permissions(db_session):
    
    perm_category = db_session.query(permission_category).all()
    permiss = []
    categ = {}
    all_data = []
    for category in perm_category:
        categ.update({"id": category.id,
                          "name": category.name})
        permissions = db_session.query(permission).filter(permission.category_id == category.id).all()
        for perm in permissions:
            permiss.append({"id":perm.id,
                            "name": perm.name and perm.name or None,
                            "endpoint": perm.route})
        all_data.append({'category':categ,
                         'permissions':permiss})
        permiss = []
        categ = {}
    return all_data


def check_permissions(path, userid, db_session):
    user = db_session.query(Users).filter(Users.id == userid).first()
    for role in user.roles:
        for permissions in role.role_permission:
            if permissions.endpoint in path:
                return "OK"
            warning(404,'Бу сахифа топилмади.')


def get_user_roles_id_by_array(id, db_session):
    get_user = db_session.query(Users).filter(Users.id == id).first()
    is_exists(get_user, 400, 'User not found!')
    roles = []
    for role in get_user.roles:
        roles.append({"id": role.id,
                      "role_name": role.name,
                      "level": role.level})
    return roles


def get_user_roles(id, db_session):
    get_user = db_session.query(Users).filter(Users.id == id).first()
    is_exists(get_user, 400, 'User not found!')
    roles = []
    if get_user.roles is not None:
        for role in get_user.roles:
            roles.append({"id":role.id,
                          "name": role.name})
    return roles


def get_user_roles_id_by_array(id, db_session):
    get_user = db_session.query(Users).filter(Users.id == id).first()
    is_exists(get_user, 400, 'User not found!')
    roles = []
    if get_user.roles is not None:
        for role in get_user.roles:
            roles.append(role.id)
    return roles



def append_user_role(userid, request, db_session):
    get_user = db_session.query(Users).filter(Users.id == userid).first()
    
    is_exists(get_user, 400, 'User not found!')
    
    current_roles = get_user_roles_id_by_array(userid, db_session)
    for new_role in request.role:
        if new_role not in current_roles:
            role = db_session.query(roles).filter(roles.id == new_role).first()
            get_user.roles.append(role)
            db_session.add(get_user)
    for role in current_roles:
        if role not in request.role:
            role = db_session.query(roles).filter(roles.id == role).first()
            get_user.roles.remove(role)
    commit_object(db_session)
    return{"result":"OK"}



def append_role_user_to_all_users(db_session):
    get_users = db_session.query(Users).all()
    role = db_session.query(roles).filter(roles.name == ("user" or "User")).first()
    for user in get_users:
        if user.roles is None or user.roles == []:
            user.roles.append(role)
            db_session.add(user)
    commit_object(db_session)
    return{"result":"OK"}


def append_role_user_to_user(id, db_session):
    user = db_session.query(Users).filter(Users.id == id).first()
    role = db_session.query(roles).filter(roles.name == ("user" or "User")).first()
    if user.roles is None or user.roles == []:
        user.roles.append(role)
        db_session.add(user)
    commit_object(db_session)
    return{"result":"OK"}


def delete_appended_user_role(user_id, db_session):
    user = db_session.query(Users).filter(Users.id == user_id).first()
    
    if user.roles:
        user.roles.clear()
        db_session.add(user)
    commit_object(db_session)
    return {"result":"OK"}




def max_user_level_by_role(id, db_session):
    get_user = db_session.query(Users).filter(Users.id == id).first()
    max_level = 0
    is_exists(get_user, 400, 'User not found!')
    
    for role in get_user.roles:
        if role.level > max_level:
            max_level = role.level
    return max_level


def compare_role_level(authorized_user_id, comparable_user_id, db_session):
    authorized_user_level = max_user_level_by_role(authorized_user_id, db_session)
    comparable_user_level = max_user_level_by_role(comparable_user_id, db_session)
    return authorized_user_level > comparable_user_level and True or False
