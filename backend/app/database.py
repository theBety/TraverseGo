#config of SQLAlchemy, ready for SQLite (local usage), later for PostgreSQL through .env

import os
from typing import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

load_dotenv() #load .env, if exists

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///.traversego.db")

# SQLite needs check_same_thread=False for working with FastAPI, PostgreSQL does not need it, so we set it conditionally
connection_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connection_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()