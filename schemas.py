from pydantic import BaseModel, EmailStr, Field
from typing import List

class UserBase(BaseModel):
    name: str
    age: int
    gender: str
    email: EmailStr  # Using EmailStr for validation
    city: str
    interests: List[str]

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int

    class Config:
        from_attributes = True
        

class DeleteResponse(BaseModel):    
    status_code: int
    detail: str

class UpdateResponse(BaseModel):
    status_code: int
    content: dict