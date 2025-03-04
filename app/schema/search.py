from pydantic import BaseModel, Field
from typing import List
from uuid import UUID

class PaperSearchRequest(BaseModel):
    query: str = Field(..., max_length=100, description="User search query (Max 100 characters)")
    num_papers: int = Field(default=5, ge=1, le=50, description="Number of papers to fetch.")
    min_year: int = Field(default=2018, ge=1900, description="Minimum publication year for search results.")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "Search papers on LLM",
                "num_papers": 10,
                "min_year": 2020
            }
        }
class PaperMetadata(BaseModel):
    paper_id: UUID = Field(..., description="Unique identifier for the research paper.")
    title: str = Field(..., description="Title of the research paper.")
    authors: str = Field(..., description="Authors of the paper.")
    summary: str = Field(..., description="Summary or abstract of the paper.")
    link: str = Field(..., description="Direct link to the research paper.")
    source: str = Field(..., description="Source database (e.g., ArXiv, PubMed).")

class PaperSearchResponse(BaseModel):
    query: str
    results: List[PaperMetadata] = Field(..., description="List of retrieved research papers.")
