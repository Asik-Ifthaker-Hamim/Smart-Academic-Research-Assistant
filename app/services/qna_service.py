import os
from sqlalchemy.orm import Session
from app.schema.qna import QnARequest, QnAResponse
from app.crud.uploaded_file import get_uploaded_files
from app.llm.qna_llm import answer_question, get_relevant_context
from app.faiss.faiss_vector_store import (
    load_vector_store, 
    save_vector_store,
    get_or_create_vectorstore
)
from app.faiss.text_extraction import extract_text_from_file
from app.core.dependencies import get_embedding_model
from app.utils.text_processing import split_text_into_chunks
from langchain.vectorstores import FAISS
from app.utils.qna_utils import format_document_references
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize embeddings
embeddings = get_embedding_model()

async def handle_document_query(request: QnARequest, uploaded_file) -> QnAResponse:
    """
    Process a document Q&A query using vector store retrieval.
    
    Args:
        request: QnA request containing query and parameters
        uploaded_file: File object containing path and metadata
    
    Returns:
        QnA response with answer and references
    """
    try:
        logger.info(f"Processing query for file ID: {request.file_id}")
        
        # Get or create vector store using file_id
        vectorstore = get_or_create_vectorstore(
            file_id=str(request.file_id),
            file_path=uploaded_file.file_path,
            embeddings=embeddings
        )
        
        if isinstance(vectorstore, str):  # Error message
            logger.error(f"Vector store error: {vectorstore}")
            return QnAResponse(
                query=request.query,
                answer=vectorstore,
                references=""
            )

        # Get relevant context
        relevant_context = await get_relevant_context(vectorstore, request.query)
        
        # Generate answer - use uploaded_file.file_name for display
        answer = await answer_question(
            relevant_context,
            request.query,
            uploaded_file.file_name,  # Use file_name from uploaded_file object
            request.word_limit
        )

        # Format references
        references = format_document_references(relevant_context)
        
        logger.info(f"Successfully processed query for file ID: {request.file_id}")
        return QnAResponse(
            query=request.query, 
            answer=answer,
            references=references
        )

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return QnAResponse(
            query=request.query,
            answer=f"Error processing request: {str(e)}",
            references=""
        )

        