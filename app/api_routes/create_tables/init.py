from fastapi import APIRouter
from app.db.create_tables import create_table

router = APIRouter(
    prefix = "", tags=["Create Tables"]
)





#Создание таблиц для суперпользователя
@router.get('/create_tables',status_code=200)
def create_tables():
    return {"OK!"}
    