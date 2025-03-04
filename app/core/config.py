from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    SERPER_API_KEY: str
    FIRECRAWL_API_KEY: str
    ENTREZ_EMAIL: str = "asikifthakerhamim75@gmail.com"
    DB_PATH: str = "search_history.db"
    FAISS_INDEX_PATH: str = "faiss_paper_index"

    # 🔹 Authentication Configurations
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")  

settings = Settings()
