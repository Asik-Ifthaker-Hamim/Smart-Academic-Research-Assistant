from uuid import UUID
from pydantic import BaseModel, Field
from typing import Optional

class QnARequest(BaseModel):
    file_id: UUID = Field(..., description="Uploaded document UUID")
    query: str = Field(..., max_length=500, description="User question about the document")
    word_limit: int = Field(default=150, ge=50, le=1000, description="Word limit for the generated answer.")

    class Config:
        json_schema_extra = {
            "example": {
                "file_id": "550e8400-e29b-41d4-a716-446655440000",
                "query": "What are the main findings of this paper?",
                "word_limit": 150
            }
        }

class QnAResponse(BaseModel):
    query: str
    answer: str = Field(..., description="Generated answer based on document content.")
    references: str = Field(default="", description="References from the document used to generate the answer.")
