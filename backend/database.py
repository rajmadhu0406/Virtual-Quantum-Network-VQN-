from sqlalchemy import create_engine, text
from fastapi import HTTPException
from sqlalchemy.orm import sessionmaker, scoped_session
from tenacity import retry, stop_after_attempt, wait_fixed
from sqlalchemy.exc import OperationalError
from config import TEST_MODE

from models import Switch
from models import Channel
from models import Base

DB_USER = 'root'
DB_PASSWORD = 'root'
DB_HOST = 'mysql'  # Assuming MySQL is the service name in your Docker Compose setup
DB_NAME = "resources"

if TEST_MODE:
    DB_NAME = "resources_test"


SQLALCHEMY_DATABASE_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:3306/{DB_NAME}"


# Create an engine that connects to MySQL without a specific database.
ADMIN_SQLALCHEMY_DATABASE_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:3306/"
admin_engine = create_engine(ADMIN_SQLALCHEMY_DATABASE_URL)

# Create the test database if it does not exist.
with admin_engine.connect() as conn:
    conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}"))
    conn.commit()


engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@retry(
    stop=stop_after_attempt(15),  # Retry 5 times
    wait=wait_fixed(15)  # Wait 2 seconds between retries
)
def connect_to_base():
    try:
        Base.metadata.create_all(bind=engine, checkfirst=True)
        return True
    except OperationalError as e:
        # Raise an exception if unable to connect to the database
        print(f"Database connection error: {e}")
        return False  # Return False instead of raising HTTPException


connect_to_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
