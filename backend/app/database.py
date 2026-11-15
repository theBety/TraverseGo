#config of SQLAlchemy, ready for SQLite (local usage), later for PostgreSQL through .env

import os
from typing import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

load_dotenv() #load .env, if exists

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///.traversego.db")

connect