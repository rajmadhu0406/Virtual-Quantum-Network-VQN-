from . import Base
from sqlalchemy import Column, Integer, String, Boolean

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, unique=True)
    firstName = Column(String(250))
    lastName = Column(String(250))
    username = Column(String(250), nullable=False, unique=True)  
    age = Column(Integer)
    institution = Column(String(250))
    email = Column(String(250), nullable=False, unique=True)   # Make email field required and unique
    hash_password = Column(String(250), nullable=False)  # Make password field required
    disabled = bool = False
