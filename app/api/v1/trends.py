from fastapi import APIRouter, HTTPException, Body, Depends
from typing import List
from app.schema.trends import ResearchTrendsRequest, ResearchTrendsResponse, TrendsHistoryResponse
from app.services.trends_service import analyze_research_trends
from app.auth.dependencies import get_current_user
from sqlalchemy.orm import Session
from app.crud import trends_history
from app.db.base_class import get_db

router = APIRouter()

@router.post("/", response_model=ResearchTrendsResponse)
def research_trends(
    request: ResearchTrendsRequest = Body(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Fetches research papers and analyzes research trends over time for authenticated users."""
    try:
        return analyze_research_trends(
            time_range=request.time_range,
            search_query=request.search_query,
            db=db,
            user_id=current_user.id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing research trends: {str(e)}")

@router.get("/history", response_model=List[TrendsHistoryResponse])
async def get_trends_history(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get trends search history for the current user"""
    history = trends_history.get_user_trends_history(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    return history

@router.get("/history/{trends_id}", response_model=TrendsHistoryResponse)
async def get_specific_trends(
    trends_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get specific trends analysis by ID"""
    result = trends_history.get_trends_by_id(db=db, trends_id=trends_id)
    if not result:
        raise HTTPException(status_code=404, detail="Trends analysis not found")
    if result.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this trends analysis")
    return result
