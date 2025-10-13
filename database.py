# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
import os

# Database URL - Change this to your PostgreSQL connection string
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost:5432/organization_db"
)

# For SQLite (development only)
# DATABASE_URL = "sqlite:///./organization.db"

# Create engine
engine = create_engine(
    DATABASE_URL,
    # Uncomment below for SQLite
    # connect_args={"check_same_thread": False},
    # poolclass=StaticPool,
    echo=True  # Set to False in production
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()