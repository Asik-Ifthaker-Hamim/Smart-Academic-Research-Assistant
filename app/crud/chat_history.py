from sqlalchemy.orm import Session
from app.models.chat_history import ChatHistory
from typing import List

def create_chat_history(
    db: Session, 
    user_id: str, 
    query: str, 
    response: str,
    references: str = None
) -> ChatHistory:
    """Create a new chat history record."""
    chat_record = ChatHistory(
        user_id=user_id,
        query=query,
        response=response,
        references=references
    )
    db.add(chat_record)
    db.commit()
    db.refresh(chat_record)
    return chat_record

def get_user_chat_history(
    db: Session, 
    user_id: str,
    skip: int = 0,
    limit: int = 50
) -> List[ChatHistory]:
    """Get chat history for a specific user."""
    return db.query(ChatHistory)\
        .filter(ChatHistory.user_id == user_id)\
        .order_by(ChatHistory.query_time.desc())\
        .offset(skip)\
        .limit(limit)\
        .all() 