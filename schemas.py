from pydantic import BaseModel, EmailStr
from typing import List

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
    name: str | None = None
    age: int | None = None
    gender: str | None = None
    email: EmailStr | None = None
    city: str | None = None
    interests: str | None = None

class User(UserBase):
    id: int

    class Config:
        orm_mode = True

class UserMatch(BaseModel):
    id: int
    name: str
    age: int
    gender: str
    city: str
    interests: List[str]

    class Config:
        orm_mode = True