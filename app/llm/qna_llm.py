from langchain.vectorstores import FAISS
from typing import List, Optional
from app.core.dependencies import get_qna_llm
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

llm = get_qna_llm()

async def get_relevant_context(vectorstore: FAISS, query: str, k: int = 4) -> str:
    """
    Retrieve relevant context from vector store based on the query.
    
    Args:
        vectorstore: FAISS vector store instance
        query: User's question
        k: Number of relevant chunks to retrieve
    
    Returns:
        String containing concatenated relevant context
    """
    try:
        docs = vectorstore.similarity_search(query, k=k)
        contexts = []
        for doc in docs:
            context = doc.page_content.strip()
            if context:
                contexts.append(context)
        
        return "\n\n".join(contexts)
    except Exception as e:
        logger.error(f"Error getting relevant context: {str(e)}")
        return ""

async def answer_question(
    context: str, 
    question: str, 
    doc_name: str, 
    word_limit: int = 150
) -> str:
    """
    Generate an answer for the question using the provided context.
    
    Args:
        context: Relevant text context
        question: User's question
        doc_name: Name of the document being queried
        word_limit: Maximum words in the response
    
    Returns:
        Generated answer
    """
    try:
        if not context.strip():
            return "No relevant context found to answer the question."

        prompt = f"""Based on the following context from the document '{doc_name}', 
        please answer the question. Keep the answer concise within {word_limit} words.
        If the answer cannot be found in the context, explicitly say so.

        Context:
        {context}

        Question: {question}

        Answer:"""

        response = await llm.apredict(prompt)
        return response.strip()

    except Exception as e:
        logger.error(f"Error generating answer: {str(e)}")
        return f"Error generating answer: {str(e)}"
