# app/database.py — Database engine and session management
from sqlmodel import Session, create_engine

from app.config import settings

# SQLite requires check_same_thread=False for FastAPI's async usage
connect_args = {"check_same_thread": False} if "sqlite" in settings.database_url else {}
engine = create_engine(settings.database_url, connect_args=connect_args, echo=settings.debug)


def get_session():
    # FastAPI dependency: yields a DB session for the request, then closes it.
    with Session(engine) as session:
        yield session
