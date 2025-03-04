import logging
from sqlalchemy.orm import Session
from app.models.user import User
from app.auth.auth import hash_password, verify_password
import uuid

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_user_by_username(db: Session, username: str) -> User:
    """Retrieve a user by username."""
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, username: str, email: str, password: str) -> User:
    """Create a new user with a hashed password."""
    existing_user = get_user_by_username(db, username)
    if existing_user:
        logger.warning(f"User {username} already exists.")
        return None
    
    hashed_password = hash_password(password)
    new_user = User(id=str(uuid.uuid4()), username=username, email=email, hashed_password=hashed_password)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    logger.info(f"User {username} registered successfully.")
    return new_user

def authenticate_user(db: Session, username: str, password: str) -> User:
    """Authenticates a user by verifying credentials."""
    user = get_user_by_username(db, username)
    if user and verify_password(password, user.hashed_password):
        logger.info(f"User {username} authenticated successfully.")
        return user
    logger.warning(f"Failed authentication attempt for {username}.")
    return None
