from sqlalchemy import Column, Integer, String
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    age = Column(Integer)
    gender = Column(String)
    email = Column(String, unique=True, index=True)
    city = Column(String)
    interests = Column(String) 

    @property
    def interests_list(self):
        return self.interests.split(",") if self.interests else []

    @interests_list.setter
    def interests_list(self, value):
        self.interests = ",".join(value) if value else ""
