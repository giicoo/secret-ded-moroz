from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from core.config import configs
from model.models import Base


engine = create_engine(configs.DB_URI, echo=False, future=True)
session_maker = sessionmaker(engine, expire_on_commit=False)

def create_tables():
    Base.metadata.create_all(bind=engine)

def get_session() -> Generator[Session]:
    with session_maker() as session:
        yield session
