from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from app.core.config import settings
from app.llm.agent import create_research_agent

def get_openai_client():
    """Returns an initialized OpenAI chat client."""
    return ChatOpenAI(temperature=0.3, model="gpt-4o", openai_api_key=settings.OPENAI_API_KEY)

def get_embedding_model():
    """Returns the OpenAI embeddings model."""
    return OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)

def get_research_agent():
    """Returns an initialized research agent."""
    return create_research_agent()

def get_qna_llm():
    """Returns an initialized OpenAI chat client for QnA."""
    return ChatOpenAI(
        model_name="gpt-4o",
        temperature=0.3,
        openai_api_key=settings.OPENAI_API_KEY
    )