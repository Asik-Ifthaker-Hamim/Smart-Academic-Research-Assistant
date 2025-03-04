from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict, Any

class ResearchTrendsRequest(BaseModel):
    time_range: str = Field(..., max_length=100, description="Time range for trend analysis (Max 100 characters)")
    search_query: str = Field(..., max_length=100, description="User query for research trends (Max 100 characters)")

    class Config:
        json_schema_extra = {
            "example": {
                "time_range": "Last 3 Years",
                "search_query": "LLM advancements in 2023"
            }
        }

class ResearchTrendsResponse(BaseModel):
    query: str
    publication_trends: Dict[str, int]
    trending_topics: Dict[str, int]
    time_range: str
    time_value: int
    time_unit: str
    summary_stats: Dict[str, Any] = Field(
        ...,
        description="Summary statistics including total papers, time category, and time period"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "query": "LLM advancements in 2024",
                "publication_trends": {"2024-02-28": 26},
                "trending_topics": {"ai": 5},
                "time_range": "Last 30 days",
                "time_value": 30,
                "time_unit": "day",
                "summary_stats": {
                    "total_papers": 100,
                    "time_category": "days",
                    "time_period": 30,
                    "date_range": "2024-01-29 to 2024-02-28"
                }
            }
        }

class TrendsHistoryResponse(BaseModel):
    id: str
    query: str
    results: Dict[str, Any]
    query_time: datetime

    class Config:
        from_attributes = True