"""
Celery Tasks for Video Analysis
Orchestrates the full pipeline: download -> process -> transcribe -> analyze
"""

import os
from datetime import datetime
from celery import Task
from sqlalchemy.orm import Session
from app.celery_app import celery_app
from app.models.database import SessionLocal
from app.models.models import AnalysisJob
from app.services.downloader import YouTubeDownloader
from app.services.media_proc import MediaProcessor
from app.services.transcriber import WhisperTranscriber
from app.services.llm_analyzer import LLMAnalyzer


class DatabaseTask(Task):
    """Base task with database session management"""
    _db = None
    
    @property
    def db(self) -> Session:
        if self._db is None:
            self._db = SessionLocal()
        return self._db
    
    def after_return(self, *args, **kwargs):
        if self._db is not None:
            self._db.close()
            self._db = None


@celery_app.task(bind=True, base=DatabaseTask, name="analyze_video")
def analyze_video_task(self, job_id: int):
    """
    Main task for analyzing a YouTube video
    
    Pipeline:
    1. Download video/audio from YouTube
    2. Extract and process audio
    3. Transcribe with Whisper
    4. Analyze with LLM
    5. Store results in database
    
    Args:
        job_id: Database ID of the AnalysisJob
    """
    
    # Get job from database
    job = self.db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
    if not job:
        raise ValueError(f"Job {job_id} not found")
    
    try:
        # Update status to processing
        job.status = "processing"
        self.db.commit()
        
        print(f"\n{'='*60}")
        print(f"🎬 Starting analysis for Job #{job_id}")
        print(f"📹 URL: {job.youtube_url}")
        print(f"{'='*60}\n")
        
        # Step 1: Download video and get metadata
        print("📥 Step 1/4: Downloading video...")
        downloader = YouTubeDownloader()
        
        # Get video info first
        video_info = downloader.get_video_info(job.youtube_url)
        job.video_title = video_info.get('title', 'Unknown')
        self.db.commit()
        
        print(f"📺 Video: {video_info['title']}")
        print(f"⏱️ Duration: {video_info.get('duration', 0)} seconds")
        
        # Download audio only (faster and smaller)
        audio_path = downloader.download_audio_only(job.youtube_url)
        print(f"✅ Audio downloaded: {audio_path}")
        
        # Step 2: Process audio
        print("\n🎵 Step 2/4: Processing audio...")
        processor = MediaProcessor()
        
        # Convert to WAV for Whisper (optional, but optimal)
        wav_path = processor.convert_to_wav(audio_path)
        print(f"✅ Audio converted to WAV: {wav_path}")
        
        # Step 3: Transcribe with Whisper
        print("\n🎤 Step 3/4: Transcribing audio...")
        transcriber = WhisperTranscriber()
        transcription_result = transcriber.transcribe(wav_path)
        
        transcription_text = transcription_result["text"]
        detected_language = transcription_result["language"]
        
        print(f"✅ Transcription complete!")
        print(f"🌍 Language: {detected_language}")
        print(f"📝 Text length: {len(transcription_text)} characters")
        print(f"📊 First 200 chars: {transcription_text[:200]}...")
        
        # Unload Whisper model to free memory
        transcriber.unload_model()
        
        # Step 4: Analyze with LLM
        print("\n🤖 Step 4/4: Analyzing content with LLM...")
        analyzer = LLMAnalyzer()
        analysis_result = analyzer.analyze_content(
            transcription=transcription_text,
            video_metadata=video_info
        )
        
        print(f"✅ Analysis complete!")
        print(f"🎯 AI Generated Score: {analysis_result['ai_generated_score']}%")
        print(f"⚠️ Dangerous Content: {analysis_result['dangerous_content']}")
        if analysis_result['dangerous_content']:
            print(f"🚨 Danger Categories: {', '.join(analysis_result['danger_categories'])}")
            print(f"📊 Severity: {analysis_result['danger_severity']}")
        
        # Step 5: Store results
        print("\n💾 Saving results to database...")
        
        # Combine all results
        final_result = {
            "video_info": video_info,
            "transcription": {
                "text": transcription_text,
                "language": detected_language,
                "segments": transcription_result.get("segments", [])
            },
            "analysis": analysis_result,
            "processed_at": datetime.utcnow().isoformat()
        }
        
        job.result = final_result
        job.status = "completed"
        job.completed_at = datetime.utcnow()
        self.db.commit()
        
        # Cleanup: Delete temporary files
        print("\n🗑️ Cleaning up temporary files...")
        try:
            if os.path.exists(audio_path):
                os.remove(audio_path)
            if os.path.exists(wav_path):
                os.remove(wav_path)
            print("✅ Cleanup complete")
        except Exception as cleanup_error:
            print(f"⚠️ Cleanup warning: {cleanup_error}")
        
        print(f"\n{'='*60}")
        print(f"✅ Job #{job_id} completed successfully!")
        print(f"{'='*60}\n")
        
        return final_result
    
    except Exception as e:
        # Handle errors
        print(f"\n❌ Error in job #{job_id}: {str(e)}")
        
        job.status = "failed"
        job.error_message = str(e)
        job.completed_at = datetime.utcnow()
        self.db.commit()
        
        # Re-raise for Celery to handle
        raise
