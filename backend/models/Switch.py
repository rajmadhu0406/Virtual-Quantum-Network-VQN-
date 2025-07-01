from sqlalchemy import Boolean, Column, Integer
from sqlalchemy.orm import relationship
from . import Base



class Switch(Base):
    __tablename__ = 'switches'
    
    id = Column(Integer, primary_key=True, unique=True)
    channels_count = Column(Integer, nullable=False)
    active = Column(Boolean, default=True)
    
    channels = relationship("models.Channel.Channel", back_populates="switch", cascade="all, delete-orphan")
