from pydantic import BaseModel, EmailStr, ValidationError
from typing import List, Optional

class UserBase(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    email: Optional[EmailStr] = None
    city: Optional[str] = None
    interests: Optional[List[str]] = None 

class UserCreate(UserBase):
    name: str
    age: int
    gender: str
    email: EmailStr
    city: str
    interests: List[str]  

class UserUpdate(UserBase): 
    pass

class User(UserBase):
    id: int

    class Config:
        from_attributes = True  

def validate_email(email: str) -> bool:
    """Validate email format manually."""
    try:
        EmailStr.validate(email)
        return True
    except ValidationError:
        return False
