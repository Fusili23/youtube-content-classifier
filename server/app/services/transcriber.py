"""
Whisper AI Transcription Service
Converts audio to text using OpenAI's Whisper model
"""

import whisper
import torch
from typing import Dict, Any, Optional
from app.core.config import settings


class WhisperTranscriber:
    """Service for transcribing audio using Whisper AI"""
    
    def __init__(self, model_size: str = None):
        """
        Initialize Whisper transcriber
        
        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
                       Defaults to settings.WHISPER_MODEL_SIZE
        """
        self.model_size = model_size or settings.WHISPER_MODEL_SIZE
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"🎤 Whisper will use device: {self.device}")
    
    def load_model(self):
        """Load Whisper model (lazy loading to save memory)"""
        if self.model is None:
            print(f"📥 Loading Whisper model: {self.model_size}")
            self.model = whisper.load_model(self.model_size, device=self.device)
            print(f"✅ Whisper model loaded")
    
    def transcribe(self, audio_path: str, language: Optional[str] = None) -> Dict[str, Any]:
        """
        Transcribe audio file to text
        
        Args:
            audio_path: Path to audio file
            language: Optional language code (e.g., 'en', 'ko', 'ja')
                     Auto-detected if None
        
        Returns:
            Dictionary with transcription results:
            - text: Full transcription text
            - language: Detected/specified language
            - segments: List of timestamped segments
        """
        # Load model if not already loaded
        self.load_model()
        
        print(f"🎙️ Transcribing audio: {audio_path}")
        
        # Transcribe with Whisper
        options = {
            "task": "transcribe",
            "verbose": False,
        }
        
        if language:
            options["language"] = language
        
        result = self.model.transcribe(audio_path, **options)
        
        print(f"✅ Transcription complete. Detected language: {result.get('language', 'unknown')}")
        
        return {
            "text": result["text"],
            "language": result.get("language", "unknown"),
            "segments": [
                {
                    "start": seg["start"],
                    "end": seg["end"],
                    "text": seg["text"]
                }
                for seg in result.get("segments", [])
            ]
        }
    
    def transcribe_with_timestamps(self, audio_path: str, language: Optional[str] = None) -> str:
        """
        Transcribe audio with timestamps in readable format
        
        Args:
            audio_path: Path to audio file
            language: Optional language code
        
        Returns:
            Formatted transcription with timestamps
        """
        result = self.transcribe(audio_path, language)
        
        # Format with timestamps
        formatted_lines = []
        for segment in result["segments"]:
            start_time = self._format_timestamp(segment["start"])
            end_time = self._format_timestamp(segment["end"])
            text = segment["text"].strip()
            formatted_lines.append(f"[{start_time} -> {end_time}] {text}")
        
        return "\n".join(formatted_lines)
    
    @staticmethod
    def _format_timestamp(seconds: float) -> str:
        """Convert seconds to MM:SS format"""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"
    
    def unload_model(self):
        """Unload model to free memory"""
        if self.model is not None:
            del self.model
            self.model = None
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            print("🗑️ Whisper model unloaded")
