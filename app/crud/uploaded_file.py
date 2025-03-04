from uuid import uuid4
from sqlalchemy.orm import Session
from app.models.uploaded_file import UploadedFile

def insert_uploaded_files(db: Session, user_id: str, file_name: str, file_path: str) -> UploadedFile:
    """Inserts a new uploaded file record with user_id."""
    new_file = UploadedFile(
        id=str(uuid4()),  # Generate new UUID
        user_id=user_id,
        file_name=file_name,
        file_path=file_path
    )
    db.add(new_file)
    db.commit()
    db.refresh(new_file)
    return new_file

def get_uploaded_files(db: Session, user_id: str):
    """Retrieves uploaded files only for the logged-in user."""
    return db.query(UploadedFile).filter(UploadedFile.user_id == user_id).all()

def get_uploaded_file(db: Session, user_id: str, file_id: str) -> UploadedFile:
    """Retrieves a specific uploaded file by UUID for the logged-in user."""
    return db.query(UploadedFile).filter(
        UploadedFile.id == str(file_id),  # Convert UUID to string if needed
        UploadedFile.user_id == user_id
    ).first()
