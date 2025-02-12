import os
from dotenv import load_dotenv

load_dotenv()

def get_openai_api_key():
    """Retrieves the OpenAI API key from the environment variables."""
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise ValueError("OpenAI API key not found.  Set the OPENAI_API_KEY environment variable.")
    return key