from app.db.base_class import Base
from app.db.session import engine

def init_db():
    """Initializes the database with all tables."""
    Base.metadata.create_all(bind=engine)
