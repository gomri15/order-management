import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
from sqlalchemy.exc import OperationalError

# Read database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://order_user:securepassword@localhost/order_db")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_size=10,  # Max connections
    max_overflow=5,  # Extra connections beyond pool_size
    pool_pre_ping=True  # Test connections before using them
)
# Scoped session to ensure thread safety
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
# Base class for ORM models
Base = declarative_base()


def get_db():
    """
    Dependency that provides a database session.
    Ensures session cleanup after each request.
    """
    db = SessionLocal()
    try:
        yield db
    except OperationalError as e:
        logger.error(f"Database connection error: {e}")
        raise
    finally:
        db.close()
