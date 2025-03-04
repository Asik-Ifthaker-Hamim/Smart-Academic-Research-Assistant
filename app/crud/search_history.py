from sqlalchemy.orm import Session
from app.models.search_history import SearchHistory

def insert_search_history(db: Session, user_id: str, paper_id: str, index_id: str, title: str, authors: str, summary: str, link: str, source: str):
    """Inserts a new record into search history with user_id if it doesn't already exist."""
    if not db.query(SearchHistory).filter(SearchHistory.paper_id == paper_id, SearchHistory.user_id == user_id).first():
        new_record = SearchHistory(
            user_id=user_id,
            paper_id=paper_id,
            index_id=index_id,
            title=title,
            authors=authors,
            summary=summary,
            link=link,
            source=source
        )
        db.add(new_record)
        db.commit()

def get_search_history(db: Session, user_id: str, index_id: str = None):
    """Retrieves search history for a specific user, optionally filtered by index_id."""
    query = db.query(SearchHistory).filter(SearchHistory.user_id == user_id)
    if index_id:
        query = query.filter(SearchHistory.index_id == index_id)
    return query.all()

def get_paper_details(db: Session, user_id: str, paper_id: str):
    """Fetches paper details for a specific user, ensuring restricted access."""
    return db.query(SearchHistory).filter(SearchHistory.paper_id == paper_id, SearchHistory.user_id == user_id).first()

def get_papers_by_index_id(db: Session, user_id: str, index_id: str):
    """Fetches all papers for a given index_id that belong to the logged-in user."""
    return db.query(SearchHistory).filter(SearchHistory.index_id == index_id, SearchHistory.user_id == user_id).all()

def get_available_index_ids(db: Session, user_id: str):
    """Fetches all distinct index_ids from search history for a specific user."""
    return db.query(SearchHistory.index_id).filter(SearchHistory.user_id == user_id).distinct().all()
