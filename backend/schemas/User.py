from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    username: Optional[str] = None
    email: EmailStr  # EmailStr enforces the email  forma
    institution: str
    age: int
    disabled: bool = False
    
class UserLogin(BaseModel):
    username: str
    password: str

class UserCreate(UserBase):
    password: str
    pass

class DBUser(UserBase):
    id: int
    hash_password: str

    class Config:
        orm_mode = True