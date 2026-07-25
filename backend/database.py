import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# By default uses local SQLite so you can run this instantly with no setup.
# For the real hackathon deploy, set DATABASE_URL to your PostgreSQL/PostGIS instance, e.g.:
# postgresql://user:password@localhost:5432/geoai
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./geoai.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
