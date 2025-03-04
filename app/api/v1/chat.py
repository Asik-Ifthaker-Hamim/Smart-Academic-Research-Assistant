from fastapi import APIRouter, HTTPException, Body, Depends
from app.schema.chat import ChatRequest, ChatResponse
from app.services.chat_service import handle_query
from app.auth.dependencies import get_current_user
from sqlalchemy.orm import Session
from app.crud.chat_history import get_user_chat_history
from app.db.base_class import get_db

router = APIRouter()

@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest = Body(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Handles research chat assistant queries for authenticated users."""
    try:
        response = await handle_query(request.query, db, current_user.id)
        return ChatResponse(query=request.query, response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@router.get("/history")
async def get_chat_history(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Retrieve chat history for the authenticated user."""
    history = get_user_chat_history(db, current_user.id, skip, limit)
    return {
        "history": [
            {
                "id": record.id,
                "query": record.query,
                "response": record.response,
                "references": record.references,
                "query_time": record.query_time
            }
            for record in history
        ]
    }
