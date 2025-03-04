from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schema.search import PaperSearchRequest, PaperSearchResponse, PaperMetadata
from app.services.search_service import search_papers
from app.crud.search_history import get_search_history
from app.auth.dependencies import get_current_user

router = APIRouter()

@router.post("/", response_model=PaperSearchResponse)
def search(
    index_id: str,
    request: PaperSearchRequest = Body(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Searches research papers from multiple sources for the authenticated user."""
    return search_papers(index_id, request, db, current_user.id)

@router.get("/history", response_model=list[PaperMetadata])
def fetch_search_history(
    index_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Retrieves search history for the logged-in user."""
    history_records = get_search_history(db, current_user.id, index_id)
    return [
        PaperMetadata(
            paper_id=record.paper_id,
            title=record.title,
            authors=record.authors,
            summary=record.summary,
            link=record.link,
            source=record.source,
            search_time=record.search_time
        )
        for record in history_records
    ]
