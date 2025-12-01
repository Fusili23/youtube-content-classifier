"""
FastAPI Main Application
Entry point for the web server
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.models.database import init_db
from app.api.endpoints import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup: Initialize database
    print("🚀 Initializing database...")
    init_db()
    print("✅ Database initialized")
    yield
    # Shutdown: Cleanup if needed
    print("👋 Shutting down...")


# Create FastAPI application
app = FastAPI(
    title="YouTube AI Content Detector API",
    description="Detect AI-generated and dangerous content from YouTube videos",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "YouTube AI Content Detector API",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
