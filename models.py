from sqlalchemy import Column, Integer, String, ARRAY
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(30), index=True)
    age = Column(Integer)
    gender = Column(String(1))
    email = Column(String(40), unique=True, index=True)
    city = Column(String(30), index=True)
    interests = Column(String(20))

