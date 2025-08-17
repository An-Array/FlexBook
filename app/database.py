from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from .config import settings

# Base class
class Base(DeclarativeBase):
  pass

# Database URL
SQLALCHEMY_DATABASE_URL= f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}"

# Database Engine
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)

# Session 
SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

# Dependency
def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()