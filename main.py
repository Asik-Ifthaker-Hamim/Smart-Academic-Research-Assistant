from fastapi import FastAPI
from app.api.v1.auth_endpoint import router as auth_router
from app.api.v1.search import router as search_router
from app.api.v1.analysis import router as analysis_router
from app.api.v1.chat import router as chat_router
from app.api.v1.qna import router as qna_router
from app.api.v1.trends import router as trends_router
from app.db.init_db import init_db

init_db()

app = FastAPI(title="Smart Academic Research Assistant", version="0.9.1")

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(search_router, prefix="/search", tags=["Search"])
app.include_router(analysis_router, prefix="/analysis", tags=["Analysis"])
app.include_router(chat_router, prefix="/chat", tags=["Chat"])
app.include_router(qna_router, prefix="/qna", tags=["QnA"])
app.include_router(trends_router, prefix="/trends", tags=["Trends"])
