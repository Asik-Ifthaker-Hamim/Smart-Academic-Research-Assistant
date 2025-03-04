from sqlalchemy.orm import Session
from app.models.trends_history import TrendsHistory
from typing import List, Optional

def create_trends_history(
    db: Session, 
    user_id: str, 
    query: str, 
    results: dict
) -> TrendsHistory:
    """Create a new trends history record."""
    db_trends = TrendsHistory(
        user_id=user_id,
        query=query,
        results=results
    )
    db.add(db_trends)
    db.commit()
    db.refresh(db_trends)
    return db_trends

def get_user_trends_history(
    db: Session, 
    user_id: str,
    skip: int = 0,
    limit: int = 10
) -> List[TrendsHistory]:
    """Get trends history for a specific user."""
    return db.query(TrendsHistory)\
        .filter(TrendsHistory.user_id == user_id)\
        .order_by(TrendsHistory.query_time.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()

def get_trends_by_id(
    db: Session,
    trends_id: str
) -> Optional[TrendsHistory]:
    return db.query(TrendsHistory).filter(TrendsHistory.id == trends_id).first() 