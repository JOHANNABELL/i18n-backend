from typing import Annotated
from fastapi import Depends
from sqlalchemy import create_engine
import psycopg2
from sqlalchemy.orm import sessionmaker, Session, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

""" You can add a DATABASE_URL environment variable to your .env file """
# DATABASE_URL = os.getenv("DATABASE_URL")

""" Or hard code SQLite here """
# DATABASE_URL = "sqlite:///./todosapp.db"

""" Or hard code PostgreSQL here """
# DATABASE_URL="postgresql://postgres:postgres@db:5432/cleanfastapi"
DATABASE_URL = "postgresql+psycopg2://postgres:felicia@localhost:5432/RHOpenLabs"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
DbSession = Annotated[Session, Depends(get_db)]

