from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from contextlib import contextmanager
from app.config.config import POSTGRES_DB, POSTGRES_HOST, POSTGRES_PASSWORD, POSTGRES_USER
from sqlalchemy.orm import sessionmaker
#asyncpg df
engine = create_engine(f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:5432/{POSTGRES_DB}",
                       query_cache_size=3600,  pool_size=100, max_overflow=10)

Base = declarative_base() 

SessionLocal = sessionmaker(bind=engine)


@contextmanager
def SessionManager():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
