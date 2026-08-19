import sys
import os

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import Base, engine
import app.models  # Import all models to ensure they are registered with Base.metadata

def init_db():
    """Create all database tables defined in SQLAlchemy ORM models."""
    print("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db()
