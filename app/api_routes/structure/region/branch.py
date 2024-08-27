from fastapi import APIRouter, Depends
import logging
from app.db.connect_db import SessionManager
from app.schemas.branch_schemas import Branch_request_schema
from app.middleware.auth_file import AuthHandler
from app.services.structure.region import region_crud
from app.services.users import attached_regions

auth_handler = AuthHandler()
router = APIRouter(
    prefix = "/branch", tags=["Region"]
)

@router.get('/v1/read/all')
def branch_page():
    with SessionManager() as db_session:
        branches = region_crud.get_all_regions(db_session)
    return branches



@router.get('/v1/get-attached-regions')
def branch_page(main_responsible:int=None, attached_type:int=None, user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        db_session.add(user)
        data = attached_regions.get_user_attached_regions(user, user.id, user.region_id, user.department, attached_type, db_session)
        #branches = region_crud.get_attached_regions(user, main_responsible, attached_type, db_session)
    return data


# @router.post('/v1/create')
# def branch_add(request: Branch_request_schema, user=Depends(auth_handler.auth_wrapper)):
#     with SessionManager() as db_session:
#         db_session.add(user)
#         logger.info("add-branch page activated!")
#         status = branch.create_branch(request.branch_number, request.branch_name, db_session)   
#     return status

# @router.put('/v1/update/{id}')
# def branch_update(id:int, request: Branch_request_schema):
#     with SessionManager() as db_session:
#         status = branch.update_branch(id, request.branch_number, request.branch_name, db_session)
#     return status

# @router.delete('/v1/delete/{id}')
# def branch_delete(id:int):
#     with SessionManager() as db_session:
#         status = branch.delete_branch(id,db_session)
#     return status