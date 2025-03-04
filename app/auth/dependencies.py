import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """Retrieves the current logged-in user from JWT and ensures user-specific access."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            logger.warning("JWT token missing 'sub' field.")
            raise credentials_exception
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            logger.warning(f"User ID {user_id} not found in the database.")
            raise credentials_exception
        logger.info(f"User {user.username} authenticated successfully.")
        return user
    except JWTError as e:
        logger.error(f"JWT decoding failed: {str(e)}")
        raise credentials_exception
