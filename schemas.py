from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict


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
    name: Optional[str] = None
    age: Optional[int] = None
    email: Optional[EmailStr] = None
    city: Optional[str] = None
    interests: Optional[List[str]] = None


class MatchDetails(BaseModel):
    age_compatibility: float
    location_compatibility: float
    interests_compatibility: float


class UserMatch(BaseModel):
    user: "User"
    compatibility_score: float
    match_details: MatchDetails


class User(UserBase):
    id: int

    class Config:
        orm_mode = True
