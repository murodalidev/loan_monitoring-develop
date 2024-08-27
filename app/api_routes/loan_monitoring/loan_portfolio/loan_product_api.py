from fastapi import APIRouter, Depends
from app.services.loan_monitoring.directories import loan_product_crud
from ....common import common_handler
from app.db.connect_db import SessionManager
from app.schemas.loan_product_schemas import LoanProduct
from app.middleware.auth_file import AuthHandler


auth_handler = AuthHandler()
router = APIRouter(
    prefix = "/loan-product", tags=["Loan Product"]
)


@router.get('/v1/read/all')
def loan_product_page(name:str=None, is_target:int=None, type:int=None, checked:bool=None, page:int=None, size:int=None):
    with SessionManager() as db_session:
        response = common_handler.handle_error(loan_product_crud.get_all_loan_products, name, is_target, type, checked, page, size, db_session)
    return response

@router.get('/v1/data-for-create/get')
def get_product_type():
    with SessionManager() as db_session:
        response = common_handler.handle_error(loan_product_crud.get_loan_product_type, db_session)
    return response



@router.post('/v1/create')
def loan_product_add(request: LoanProduct, user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        db_session.add(user)
        response = common_handler.handle_error(loan_product_crud.create_loan_product, request, user.username, db_session)
    return response



@router.put('/v1/update/{id}')
def loan_product_update(id:int, request: LoanProduct, user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        db_session.add(user)
        response = common_handler.handle_error(loan_product_crud.update_loan_product, id, request, user.username, db_session)
    return response


@router.delete('/v1/delete/{id}')
def loan_product_delete(id:int, user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        db_session.add(user)
        response = common_handler.handle_error(loan_product_crud.delete_loan_product, id, user.username, db_session)
    return response


@router.get('/v1/update/loan-products')
def update_loan_product():
    with SessionManager() as db_session:
        response = common_handler.handle_error(loan_product_crud.update_loan_product_table, db_session)
    return response