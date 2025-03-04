from pydantic import BaseModel, Field
from typing import List, Dict
from uuid import UUID

from app.crud.search_history import  get_papers_by_index_id

class PaperSelectionEnum(str):
    """Dynamically fetch available papers by selected index_id."""
    @classmethod
    def get_papers(cls, index_id: str) -> Dict[str, str]:
        papers = get_papers_by_index_id(index_id)
        return {paper["paper_id"]: paper["title"] for paper in papers}
    
class AnalysisRequest(BaseModel):
    selected_paper_ids: List[UUID] = Field(..., description="List of selected paper UUIDs for analysis.")
    sections: List[str] = Field(default=["Abstract", "Introduction", "Conclusion"], description="Sections to include in the analysis.")
    word_limit: int = Field(default=300, ge=100, le=5000, description="Word limit for the generated analysis report.")

    class Config:
        json_schema_extra = {
            "example": {
                "selected_paper_ids": ["550e8400-e29b-41d4-a716-446655440000"],
                "sections": ["Abstract", "Conclusion"],
                "word_limit": 200
            }
        }

class AnalysisResponse(BaseModel):
    report: str = Field(..., description="Generated comparative analysis report.")
