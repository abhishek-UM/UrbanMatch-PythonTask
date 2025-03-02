from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# // Free to use remote db or create a local database. Modify the URl appropriately
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Is responsible for FastApi to interact with database
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# It is responsible for interacting with db
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# It can be commonly used by all classes
Base = declarative_base()

