from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base  # Updated import

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()  # Updated to use SQLAlchemy 2.0 convention
