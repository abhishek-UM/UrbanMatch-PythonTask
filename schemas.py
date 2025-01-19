from typing import List, Optional
from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    name: str
    age: int
    gender: str
    email: EmailStr
    city: str
    interests: str

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    email: Optional[EmailStr] = None
    city: Optional[str] = None
    interests: Optional[str] = None

class User(UserBase):
    id: int

    class Config:
        orm_mode = True

class MatchRequirements(BaseModel):
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    city: Optional[str] = None
