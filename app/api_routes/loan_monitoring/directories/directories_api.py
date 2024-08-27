from fastapi import APIRouter, Depends
from app.db.connect_db import SessionManager
from ....services.loan_monitoring.directories import load_all_from_files, loan_product_crud
from ....services.loan_monitoring.directories import local_code_crud
router = APIRouter(
    prefix = "/directories", tags=["Directories"]
)

@router.get('/v1/load-post-codes-db/all')
def portrfolio():
    with SessionManager() as db_session:
        load_all_from_files.load_dist_post_codes(db_session)
    return {'OK'}


@router.get('/v1/load-loan-product-db/all')
def portrfolio():
    with SessionManager() as db_session:
        loan_product_crud.load_loan_product(db_session)
    return {'OK'}





@router.get('/v1/load-directories-db/all')
def portrfolio():
    with SessionManager() as db_session:
        load_all_from_files.load_directories(db_session)
    return {'OK'}



@router.get('/v1/client_region/get/all')
def get_client_region():
    with SessionManager() as db_session:
        result = load_all_from_files.get_client_region(db_session)
    return result



@router.get('/v1/bank-mfo/get/all')
def get_client_region(region_id:int):
    with SessionManager() as db_session:
        result = load_all_from_files.get_bank_mfo_by_region(region_id,db_session)
    return result