from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from app.auth.auth import create_access_token
from app.crud.auth_crud import create_user, authenticate_user
from app.db.session import get_db
import logging

router = APIRouter(tags=["Authentication"])

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.post("/register")
def register(username: str, email: str, password: str, db: Session = Depends(get_db)):
    """Registers a new user."""
    new_user = create_user(db, username, email, password)
    if not new_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    return {"message": "User registered successfully"}

@router.post("/token")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """OAuth2 compatible token login, get an access token for future requests."""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        logger.warning(f"Login failed for user {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token({"sub": user.id}, timedelta(minutes=30))
    logger.info(f"User {form_data.username} logged in successfully")
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username
    }