from sqlalchemy import Column, Integer, String, Boolean, Text
from database import Base
import json

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    age = Column(Integer)
    gender = Column(String)
    email = Column(String, unique=True, index=True)
    city = Column(String, index=True)
    interests = Column(Text, nullable=True)  # Store as JSON text
    is_deleted = Column(Boolean, default=False)

    def set_interests(self, interests_list):
        self.interests = json.dumps(interests_list)

    def get_interests(self):
        return json.loads(self.interests) if self.interests else []
