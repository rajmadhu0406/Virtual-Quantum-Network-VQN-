from pydantic import BaseModel
from typing import Optional

class Switch(BaseModel):
    channels_count: int
    active: Optional[bool] = False
    
class DBSwitch(BaseModel):
    id: int
    channels_count: int
    active: bool
    
    class Config:
        orm_mode = True