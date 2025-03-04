from app.core.dependencies import get_research_agent
from app.crud.chat_history import create_chat_history
from app.utils.chat_utils import format_references
from sqlalchemy.orm import Session

async def handle_query(query: str, db: Session, user_id: str) -> str:
    """Processes a user query via the research chat assistant."""
    agent, ref_tracker = get_research_agent()
    
    try:
        response = agent.run(query).strip()
        references = format_references(ref_tracker)
        
        # Store in database
        create_chat_history(
            db=db,
            user_id=user_id,
            query=query,
            response=response,
            references=references
        )

        response += references
        return response
    except Exception as e:
        return f"Error processing query: {str(e)}"
