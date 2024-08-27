from fastapi import APIRouter, Depends
from app.services.loan_monitoring.directories import lending_type_crud
from ....common import common_handler
from app.db.connect_db import SessionManager
from app.schemas.loan_product_schemas import LoanProduct
from app.middleware.auth_file import AuthHandler


auth_handler = AuthHandler()
router = APIRouter(
    prefix = "/lending-type", tags=["Lending Type"]
)


@router.get('/v1/read/all')
def loan_product_page():
    with SessionManager() as db_session:
        response = lending_type_crud.get_lending_type(db_session)
    return response

# @router.get('/v1/data-for-create/get')
# def get_product_type():
#     with SessionManager() as db_session:
#         response = common_handler.handle_error(loan_product_crud.get_loan_product_type, db_session)
#     return response



# @router.post('/v1/create')
# def loan_product_add(request: LoanProduct):
#     with SessionManager() as db_session:
#         response = common_handler.handle_error(loan_product_crud.create_loan_product, request, db_session)
#     return response



# @router.put('/v1/update/{id}')
# def loan_product_update(id:int, request: LoanProduct):
#     with SessionManager() as db_session:
#         response = common_handler.handle_error(loan_product_crud.update_loan_product, id, request, db_session)
#     return response


# @router.delete('/v1/delete/{id}')
# def loan_product_delete(id:int):
#     with SessionManager() as db_session:
#         response = common_handler.handle_error(loan_product_crud.delete_loan_product, id, db_session)
#     return response


# @router.get('/v1/update/loan-products')
# def update_loan_product():
#     with SessionManager() as db_session:
#         response = common_handler.handle_error(loan_product_crud.update_loan_product_table, db_session)
#     return response