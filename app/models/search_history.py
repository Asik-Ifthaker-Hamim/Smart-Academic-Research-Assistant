from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class SearchHistory(Base):
    __tablename__ = "search_history"

    paper_id = Column(String, primary_key=True, index=True)  
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    index_id = Column(String, index=True)
    title = Column(Text)
    authors = Column(Text)
    summary = Column(Text)
    link = Column(Text)
    source = Column(String)
    search_time = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="search_history")
