from fastapi import APIRouter, Query, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schema.analysis import AnalysisRequest, AnalysisResponse
from app.services.analysis_service import generate_analysis_report
from app.crud.search_history import get_papers_by_index_id
from app.auth.dependencies import get_current_user

router = APIRouter()

@router.get("/paper-options/")
def get_paper_options(
    index_id: str = Query(..., description="Select an index_id to fetch corresponding papers"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Returns available papers for a given `index_id` for the logged-in user."""
    try:
        papers = get_papers_by_index_id(db, current_user.id, index_id)
        if not papers:
            raise HTTPException(status_code=404, detail="No papers found for the given index_id.")
        return {"papers": {paper.paper_id: paper.title for paper in papers}}   
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching paper options: {str(e)}")

@router.post("/", response_model=AnalysisResponse)
def analyze(
    request: AnalysisRequest = Body(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Generates a comparative analysis report from selected papers for the logged-in user."""
    try:
        return generate_analysis_report(
            user_id=current_user.id,
            selected_paper_ids=request.selected_paper_ids,
            sections=request.sections,
            db=db,
            word_limit=request.word_limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating analysis report: {str(e)}")
