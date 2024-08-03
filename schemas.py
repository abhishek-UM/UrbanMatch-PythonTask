from pydantic import BaseModel, EmailStr
from typing import List, Optional

class UserBase(BaseModel):
    name: str
    age: int
    gender: str
    email: EmailStr
    city: str
    interests: List[str]

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    name: Optional[str]
    age: Optional[int]
    gender: Optional[str]
    email: Optional[EmailStr]
    city: Optional[str]
    interests: Optional[List[str]]

class User(UserBase):
    id: int

    class Config:
        orm_mode = True
