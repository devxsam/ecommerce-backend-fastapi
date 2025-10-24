"""
This file is the SQLAlchemy setup script which configures how the FastAPI application connects and interacts with the PostgreSQL database.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os


SQLALCHEMY_DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://user:pass@localhost:5432/db")


engine = create_engine(SQLALCHEMY_DATABASE_URL)
"""
This doesn't represent a single connection but a pool of connection and manages how to talk to postgresql. 
Every time the application needs to talk to the database, it uses the connection managed by this engine.
"""


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
"""
When the get_db() is called, it executes sessionlocal() to create a fresh isolated database session.
Autocommit is crucial for atomicity. means if any changes are made are not permanent until we explicitly commit it using db.commit().
False autoflush means they are not synced to sql unless we do it.
bind will link the session to the database.
"""


def get_db():
    # Dependency function is to get DB session for each request.

    db = SessionLocal()  # New independent function session from session factory will be created
    # If error occurs the db session is still closed during request handling.

    try:
        # Pauses and returns the database session object to endpoint function that is called.
        yield db
    finally:  # Always run
        db.close()


Base = declarative_base()

"""
by inheriting from Base, the User class instantly gains all the features required to be an ORM model: to map to a SQL table, 
run queries, and manage relationships with other models.
"""