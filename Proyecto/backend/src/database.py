"""
Database configuration module for the Naurat Importation Bot API.

This module sets up the SQLAlchemy database connection, session management, and base model definition.

Features:
- Establishes a connection to the database using SQLAlchemy's `create_engine`.
- Configures connection pooling for optimized performance.
- Provides a session factory (`SessionLocal`) for database interactions.
- Defines a base class (`Base`) for ORM models.
- Includes a dependency function (`get_db`) for handling database sessions in FastAPI.

Environment Variables:
- `DATABASE_URL`: The database connection string.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine(
    os.getenv("DATABASE_URL"),
    pool_size=15,
    max_overflow=20,
    pool_timeout=30,
    pool_pre_ping=True
)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base = declarative_base()


def get_db():
    """
    Provides a database session for dependency injection in FastAPI routes.

    This function yields a database session and ensures proper cleanup by closing the session
    after use.

    Yields:
        sqlalchemy.orm.Session: A database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
