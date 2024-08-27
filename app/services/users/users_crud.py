
from ...models.users.users import Users as user
from ...models.brief_case.directories.bank_mfo import bank_mfo as BankMfo
from ...models.brief_case.directories.local_code import local_code as local_codes
from ...models.brief_case.directories.client_region import client_region
from ...middleware.auth_file import AuthHandler
from ...common.commit import commit_object
from ...common.is_empty import is_empty, is_exists, warning
from ..structure.region import region_crud
from ..loan_monitoring.directories import local_code_crud
from sqlalchemy import func
from ..structure.department import department_crud
from ..structure.position import position_crud
from app.services.rbac import roles, permission_crud
from ...config.logs_config import info_logger
class Users():
    def __init__(self, data=None, aim = None):
        self.auth_handler = AuthHandler()
        if data:
            self.username=data.username and data.username or None
            self.full_name=data.full_name and data.full_name or None
            self.region_id = data.region_id and data.region_id or None
            self.local_code = data.local_code and data.local_code or None
            self.department = data.department and data.department or None
            self.position = data.position and data.position or None
            self.head = data.head and data.head or None
            self.status = data.status and data.status or None
            self.pinfl = data.pinfl and data.pinfl or None
            if aim=='create' or 'reset':
                self.password=self.auth_handler.get_password_hash('12345')
            if aim=='update':
                self.password=data.password and data.password or None
    
    
    
    def create(self,db_session):
        get_user = db_session.query(user).filter(user.username == self.username).first()
        is_empty(get_user, 400, 'username is taken!')
        
        new_user = user(
            username=self.username,
            password=self.password,
            full_name=self.full_name,
            region_id = self.region_id,
            local_code = self.local_code,
            department = self.department,
            position = self.position,
            head = self.head,
            status = 1,
            password_status = 1,
            pinfl = self.pinfl
        )
        db_session.add(new_user)
        
        commit_object(db_session)
        
        return {"status": "OK"}
    
    
    
    def update(self, id, db_session):
        # get_user= db_session.query(user).filter(user.username == self.username).first()
        # is_empty(get_user, 400, 'User has already created!')
        get_user = db_session.query(user).filter(user.id == id).first()
        if get_user is not None:
            if self.head == get_user.id:
                warning('400', 'user cannot be self head!')
            if self.username is not None:
                get_user.username=self.username
            if self.full_name is not None:
                get_user.full_name=self.full_name
            if self.region_id is not None:
                get_user.region_id = self.region_id
            if self.local_code is not None:
                get_user.local_code = self.local_code
            if self.department is not None:
                get_user.department = self.department
            if self.position is not None:
                get_user.position = self.position
            if self.head is not None:
                get_user.head = self.head
            if self.status is not None:
                get_user.status = self.status
            if self.pinfl is not None:
                get_user.pinfl = self.pinfl
            commit_object(db_session)
        else: return {"result":"User not Found"}
        return {"result":"OK"}
    
    
    def update_login_password(self, id, db_session):
        get_user= db_session.query(user).filter(user.username == self.username).first()
        is_empty(get_user, 400, 'Вы не поменяли логин!')
        get_user = db_session.query(user).filter(user.id == id).first()
        if get_user is not None:
            
            if self.username is not None:
                get_user.username=self.username
            if self.password is not None:
                get_user.password=self.auth_handler.get_password_hash(self.password)
            
            commit_object(db_session)
        else: return {"result":"User not Found"}
        return {"result":"OK"}
    
    def save_user_token_and_ip(get_user, access_token, real_ip, db_session):
        get_user.token = access_token.decode("utf-8")
        get_user.real_ip = real_ip and real_ip or None
        db_session.add(get_user)
        commit_object(db_session)
        return 0
    
    
    def get_all_data_for_user(data, db_session):
        employees = {"id":data.id,
                    "username":data.username,
                    "full_name":data.full_name,
                    "user_type": roles.get_user_roles(data.id, db_session),
                    "user_status":data.status,
                    "department":data.department and data.depart or None,
                    "region":data.region_id and data.region or None,
                    "local_code":data.local_code and data.local or None,
                    "position":data.pos.name,
                    "pinfl":data.pinfl and data.pinfl or None,
                    "head":data.head and data.heads.full_name or None,
                    "roles": permission_crud.get_user_permissions(data.id, db_session)
                    }
        return employees 
    
    
    

        
    def get_all(db_session, params=None):
        users = []
        get_user = db_session.query(user)
        if params is not None:
            get_user = get_user.filter(user.region_id ==params['region_id']).filter(user.department == params['department_id'])
        get_user = get_user.all()
        if get_user is not None:
            for us in get_user:
                users.append({"id": us.id,
                            "username": us.username,
                            "full_name": us.full_name,
                            "region_id": us.region_id and us.region or None,
                            "local_code":us.local_code and us.local or None,
                            "department":us.department and us.depart or None,
                            "position":us.position and us.pos or None})
        return users
    
    
    def get_users_by_param(size, page, full_name, user_name, region_id, local_code, department, position, db_session):
        users = []
        get_user = db_session.query(user)
        if full_name is not None:
            get_user = get_user.filter(func.lower(user.full_name).like(f'%{full_name.lower()}%'))
        if user_name is not None:
            get_user = get_user.filter(func.lower(user.username).like(f'%{user_name.lower()}%'))
        if region_id is not None:
            get_user = get_user.filter(user.region_id == region_id)
        if local_code is not None:
            get_user = get_user.filter(user.local_code == local_code)
        if department is not None:
            get_user = get_user.filter(user.department ==department)
        if position is not None:
            get_user = get_user.filter(user.position ==position)
        
        count = get_user.count()
        get_user = get_user.limit(size).offset((page-1)*size).all()
        
        if get_user is not None:
            for us in get_user:
                users.append({"id": us.id,
                            "username": us.username,
                            "full_name": us.full_name,
                            "region_id": us.region_id and us.region or None,
                            "local_code":us.local_code and us.local or None,
                            "department":us.department and us.depart or None,
                            "position":us.position and us.pos or None})
        return {"items":users,
                "total":count,
                "page":page,
                "size":size}
    
    
    
    def get_user_by_local(user_id, local_code, department, db_session, attached_type_id=None):
        users = []
        get_user = db_session.query(user).filter(user.local_code == local_code)
        
        if attached_type_id is not None:
            if attached_type_id == 2 or attached_type_id == 3:
                department = 3
            elif attached_type_id == 1:
                department = 2
            else:
                department = 4
        
        
        if department is not None:
            print(department)
            get_user = get_user.filter(user.department == department)
        
        get_user = get_user.all()
        if get_user is not None:
            for us in get_user:
                if user_id != us.id:
                    users.append({"id": us.id,
                              "username": us.username,
                              "full_name": us.full_name,
                              "region_id": us.region_id and us.region or None,
                                "local_code":us.local_code and us.local or None,
                                "department":us.department and us.depart or None,
                                "position":us.position and us.pos or None})
        return users
    
    

    def delete(self, id, db_session):
        get_user = db_session.query(user).filter(user.id == id).first()
        is_exists(get_user, 400, 'User has already created!')
        db_session.delete(get_user)
        commit_object(db_session)
        return {"result":"OK"}
    
    
    def get_user_by_id(id, db_session):
        user_data = {}
        get_user = db_session.query(user).filter(user.id == id).first()
        if get_user is not None:
            user_data = {"id": get_user.id,
                        "username": get_user.username,
                        "full_name": get_user.full_name,
                        "region_id": get_user.region_id and get_user.region or None,
                        "local_code":get_user.local_code and get_user.local or None,
                        "department":get_user.department and get_user.depart or None,
                        "position":get_user.position and get_user.pos or None}
        return user_data

    #TODO: reset passwor, change password
    
    def check_password(self, session_user, old_password):
        return self.auth_handler.verify_password(old_password, session_user.password)
        
    
    def update_password(self, session_user, old_password, db_session):
        if self.check_password(session_user, old_password):
            if self.password is not None:
                session_user.password=self.auth_handler.get_password_hash(self.password)
            commit_object(db_session)
        else: warning(400, "Invalid password")
        return {"result":"OK"}
    
    def update_username(self, session_user, db_session):
        if session_user.username == self.username:
            warning(400, 'Вы не поменяли имя пользователя или оно занято!')
        if self.username is not None:
            session_user.username=self.username
        commit_object(db_session)
        return {"result":"OK"}

    def refresh_password(self, session_user, updated_user_id, db_session):
        get_user = db_session.query(user).filter(user.id == updated_user_id).first()
        get_user.password=self.password
        commit_object(db_session)
        info_logger.info(f"password for user with id = {updated_user_id} updated by {session_user.username} {session_user.id}")
        return {"result":"OK"}
    

def get_data_for_crud(db_session):
    return {"locals": local_code_crud.get_all_local_codes(db_session),
            "departments": department_crud.get_all_departments(db_session),
            "positions": position_crud.get_all_positions(db_session),
            "users": Users.get_all(db_session)}
        
        
        
