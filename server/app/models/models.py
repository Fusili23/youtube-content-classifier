"""
Database Models
SQLAlchemy ORM models for the application
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.sql import func
from .database import Base


class AnalysisJob(Base):
    """Model for tracking video analysis jobs"""
    
    __tablename__ = "analysis_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    youtube_url = Column(String, nullable=False)
    video_title = Column(String, nullable=True)
    
    # Job status: "pending", "processing", "completed", "failed"
    status = Column(String, default="pending", nullable=False)
    
    # Analysis results stored as JSON
    result = Column(JSON, nullable=True)
    
    # Error message if job failed
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<AnalysisJob(id={self.id}, url={self.youtube_url}, status={self.status})>"
