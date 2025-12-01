"""
API Endpoints
REST API routes for video analysis
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, HttpUrl
from sqlalchemy.orm import Session
from typing import Optional
from app.models.database import get_db
from app.models.models import AnalysisJob
from app.worker.tasks import analyze_video_task


router = APIRouter()


# Request/Response Models
class AnalyzeRequest(BaseModel):
    """Request model for video analysis"""
    youtube_url: HttpUrl
    
    class Config:
        json_schema_extra = {
            "example": {
                "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            }
        }


class AnalyzeResponse(BaseModel):
    """Response model for analysis submission"""
    job_id: int
    status: str
    message: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "job_id": 123,
                "status": "pending",
                "message": "Analysis job submitted successfully"
            }
        }


class StatusResponse(BaseModel):
    """Response model for job status"""
    job_id: int
    youtube_url: str
    video_title: Optional[str]
    status: str
    created_at: str
    completed_at: Optional[str]
    error_message: Optional[str]


class ResultResponse(BaseModel):
    """Response model for analysis results"""
    job_id: int
    youtube_url: str
    video_title: Optional[str]
    status: str
    result: Optional[dict]
    error_message: Optional[str]
    created_at: str
    completed_at: Optional[str]


# Endpoints

@router.post("/analyze", response_model=AnalyzeResponse)
async def submit_analysis(
    request: AnalyzeRequest,
    db: Session = Depends(get_db)
):
    """
    Submit a YouTube video URL for analysis
    
    The video will be:
    1. Downloaded from YouTube
    2. Transcribed using Whisper AI
    3. Analyzed for AI-generated content
    4. Checked for dangerous/harmful content
    
    Returns a job_id to check status and results
    """
    
    # Create new analysis job in database
    job = AnalysisJob(
        youtube_url=str(request.youtube_url),
        status="pending"
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    
    # Submit task to Celery worker (async)
    analyze_video_task.delay(job.id)
    
    return AnalyzeResponse(
        job_id=job.id,
        status=job.status,
        message="Analysis job submitted successfully. Use the job_id to check status."
    )


@router.get("/status/{job_id}", response_model=StatusResponse)
async def get_analysis_status(
    job_id: int,
    db: Session = Depends(get_db)
):
    """
    Check the status of an analysis job
    
    Status can be:
    - pending: Job is waiting in queue
    - processing: Job is currently being processed
    - completed: Job finished successfully
    - failed: Job encountered an error
    """
    
    job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    return StatusResponse(
        job_id=job.id,
        youtube_url=job.youtube_url,
        video_title=job.video_title,
        status=job.status,
        created_at=job.created_at.isoformat() if job.created_at else None,
        completed_at=job.completed_at.isoformat() if job.completed_at else None,
        error_message=job.error_message
    )


@router.get("/result/{job_id}", response_model=ResultResponse)
async def get_analysis_result(
    job_id: int,
    db: Session = Depends(get_db)
):
    """
    Get the full analysis results for a completed job
    
    Returns video info, transcription, and AI/danger analysis results
    Only available when status is "completed"
    """
    
    job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    if job.status == "pending" or job.status == "processing":
        raise HTTPException(
            status_code=202, 
            detail=f"Job is still {job.status}. Please check back later."
        )
    
    return ResultResponse(
        job_id=job.id,
        youtube_url=job.youtube_url,
        video_title=job.video_title,
        status=job.status,
        result=job.result,
        error_message=job.error_message,
        created_at=job.created_at.isoformat() if job.created_at else None,
        completed_at=job.completed_at.isoformat() if job.completed_at else None
    )


@router.get("/jobs", response_model=list[StatusResponse])
async def list_jobs(
    limit: int = 20,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List recent analysis jobs
    
    Optional filters:
    - limit: Maximum number of jobs to return (default 20)
    - status: Filter by status (pending, processing, completed, failed)
    """
    
    query = db.query(AnalysisJob).order_by(AnalysisJob.created_at.desc())
    
    if status:
        query = query.filter(AnalysisJob.status == status)
    
    jobs = query.limit(limit).all()
    
    return [
        StatusResponse(
            job_id=job.id,
            youtube_url=job.youtube_url,
            video_title=job.video_title,
            status=job.status,
            created_at=job.created_at.isoformat() if job.created_at else None,
            completed_at=job.completed_at.isoformat() if job.completed_at else None,
            error_message=job.error_message
        )
        for job in jobs
    ]
