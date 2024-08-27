from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
from contextlib import contextmanager
from sqlalchemy.engine.url import URL
import cx_Oracle
#from app.config.config import IABS_TEST_HOST, IABS_TEST_PORT, IABS_TEST_USER, IABS_TEST_PASSWORD, IABS_TEST_DB, IABS_TEST_SERVICE_NAME
from app.config.config import IABS_HOST, IABS_PORT, IABS_USER, IABS_PASSWORD, IABS_DB, IABS_SERVICE_NAME


#test_engine = create_engine(f"oracle+cx_oracle://{IABS_TEST_USER}:{IABS_TEST_PASSWORD}@{IABS_TEST_HOST}:{IABS_TEST_PORT}/?service_name={IABS_TEST_SERVICE_NAME}")
engine = create_engine(f"oracle+cx_oracle://{IABS_USER}:{IABS_PASSWORD}@{IABS_HOST}:{IABS_PORT}/?service_name={IABS_SERVICE_NAME}")
#oracle_engine = create_engine(connect_url, max_identifier_length=128)

Base = declarative_base()
OracleSessionLocal = sessionmaker(bind=engine)

@contextmanager
def OracleSessionManager():
    oracle_session = OracleSessionLocal()
    try:
        yield oracle_session
    finally:
        oracle_session.close()