from langchain_openai import ChatOpenAI
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from app.core.config import settings
def create_chat_llm():
    """Creates and configures the ChatOpenAI instance."""
    return ChatOpenAI(
        model_name="gpt-4o",
        temperature=0.7,
        streaming=True,
        callbacks=[StreamingStdOutCallbackHandler()],
        openai_api_key=settings.OPENAI_API_KEY,
    )