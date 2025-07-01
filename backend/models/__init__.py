from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

from .Switch import Switch
from .Channel import Channel
from .User import User
from .Request import Request

