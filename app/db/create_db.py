from app.db.connect import Base, engine
from app.models.loan import Loan

print("Creating db...")

def create_table():
    return Base.metadata.create_all(engine)
