from pydantic import BaseModel
from typing import List


class UserBase(BaseModel):
    name: str
    age: int
    gender: str
    email: str
    city: str
    interests: List[str]

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int

    class Config:
        orm_mode = True

# New schema: used to identify a user by name and email
class UserIdentifier(BaseModel):
    name: str
    email: str



# Define the CandidateSuggestion schema for match suggestions
class CandidateSuggestion(BaseModel):
    id: int
    name: str
    email: str
    age: int
    gender: str
    city: str
    interests: List[str]
    match_percentage: float  # Compatibility rating as a percentage

    class Config:
        orm_mode = True



