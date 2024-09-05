from sqlalchemy import Column, Integer, String, ARRAY
from sqlalchemy.types import TypeDecorator, String
from database import Base
import json

class JSONType(TypeDecorator):
    impl = String

    def process_bind_param(self, value, dialect):
        if value is not None:
            print(value)
            print(type(value))
            return json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return json.loads(value)
        return value

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    age = Column(Integer)
    gender = Column(String)
    email = Column(String, unique=True, index=True)
    city = Column(String, index=True)
    interests = Column(JSONType)

