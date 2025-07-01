from pydantic import BaseModel, conint
from typing import Optional, List

class Channel(BaseModel):
    channel_number: int
    channel_active: Optional[bool] = False
    channel_user: Optional[str]
    switch_id: int

class DBChannel(BaseModel):
    id: int
    channel_number: int
    channel_active: Optional[bool] = False
    channel_user: Optional[str]
    switch_id: int
    
    class Config:
        orm_mode = True


class DBChannelList(BaseModel):
    channel_list: List[DBChannel]
    
    class Config:
        orm_mode = True
        
# def convert_to_pydantic_model(db_channels: List[YourSQLAlchemyModel]) -> DBChannelList:
#     pydantic_channels = [DBChannel(**channel.__dict__) for channel in db_channels]
#     return DBChannelList(channel_list=pydantic_channels)


class ChannelRequest(BaseModel):
    username: str
    channels_needed: conint(ge=0, le=100)
    switch_ids: Optional[list] = None
    