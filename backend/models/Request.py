from . import Base
from sqlalchemy import Column, Integer, String, Enum, ForeignKey, JSON

class Request(Base):
    __tablename__ = 'requests'
    
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    req_string = Column(String(250), nullable=False, unique=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    status = Column(
        Enum('processing', 'processed', 'completed', name='status_enum'),
        nullable=False,
        default='processing'
    )
    # Use a JSON column to store a list of integers corresponding to resource IDs.
    resource_ids = Column(JSON, nullable=True)

    def __repr__(self):
        return (f"<Request(req_number='{self.req_number}', username='{self.username}', "
                f"status='{self.status}', resource_ids={self.resource_ids})>")
