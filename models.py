from sqlalchemy import Column, Integer, String, ARRAY
from database import Base, engine
from sqlalchemy.types import JSON


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    age = Column(Integer)
    gender = Column(String)
    email = Column(String, unique=True, index=True)
    city = Column(String, index=True)
    interests = Column(JSON)

# used to create tables in database

# Base.metadata.createAll(bird=engine)

