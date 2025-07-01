from sqlalchemy import Column, Integer, Boolean, String, ForeignKey
from sqlalchemy.orm import relationship
from . import Base



class Channel(Base):
    __tablename__ = 'channels'
    
    id = Column(Integer, primary_key=True, unique=True)
    channel_number = Column(Integer)
    channel_active = Column(Boolean, default=False)
    channel_user = Column(String(250))
    switch_id = Column(Integer, ForeignKey('switches.id', ondelete="CASCADE"), nullable=False)  # Define foreign key to 'switches' table

    # Define relationship with Switch model
    switch = relationship("models.Switch.Switch", back_populates="channels")

