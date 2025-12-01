"""
Media Processing Service
Uses FFmpeg for audio/video manipulation
"""

import os
import ffmpeg
from typing import Optional


class MediaProcessor:
    """Service for processing media files with FFmpeg"""
    
    @staticmethod
    def extract_audio(video_path: str, output_path: str = None) -> str:
        """
        Extract audio from video file
        
        Args:
            video_path: Path to input video file
            output_path: Path for output audio file (auto-generated if None)
            
        Returns:
            Path to extracted audio file
        """
        if output_path is None:
            base_name = os.path.splitext(video_path)[0]
            output_path = f"{base_name}_audio.mp3"
        
        try:
            stream = ffmpeg.input(video_path)
            stream = ffmpeg.output(stream, output_path, acodec='libmp3lame', audio_bitrate='192k')
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            return output_path
        except ffmpeg.Error as e:
            raise Exception(f"FFmpeg error during audio extraction: {e.stderr.decode()}")
    
    @staticmethod
    def convert_to_wav(audio_path: str, output_path: str = None, sample_rate: int = 16000) -> str:
        """
        Convert audio to WAV format (optimal for Whisper)
        
        Args:
            audio_path: Path to input audio file
            output_path: Path for output WAV file (auto-generated if None)
            sample_rate: Target sample rate in Hz (Whisper works best with 16kHz)
            
        Returns:
            Path to converted WAV file
        """
        if output_path is None:
            base_name = os.path.splitext(audio_path)[0]
            output_path = f"{base_name}.wav"
        
        try:
            stream = ffmpeg.input(audio_path)
            stream = ffmpeg.output(
                stream,
                output_path,
                acodec='pcm_s16le',
                ar=sample_rate,
                ac=1  # Mono audio
            )
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            return output_path
        except ffmpeg.Error as e:
            raise Exception(f"FFmpeg error during WAV conversion: {e.stderr.decode()}")
    
    @staticmethod
    def trim_audio(audio_path: str, output_path: str = None, 
                   start_time: float = 0, duration: float = None) -> str:
        """
        Trim audio to specific duration (useful for testing or processing limits)
        
        Args:
            audio_path: Path to input audio file
            output_path: Path for output file (auto-generated if None)
            start_time: Start time in seconds
            duration: Duration in seconds (None = until end)
            
        Returns:
            Path to trimmed audio file
        """
        if output_path is None:
            base_name = os.path.splitext(audio_path)[0]
            output_path = f"{base_name}_trimmed.mp3"
        
        try:
            stream = ffmpeg.input(audio_path, ss=start_time)
            if duration:
                stream = ffmpeg.output(stream, output_path, t=duration, acodec='copy')
            else:
                stream = ffmpeg.output(stream, output_path, acodec='copy')
            
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            return output_path
        except ffmpeg.Error as e:
            raise Exception(f"FFmpeg error during audio trimming: {e.stderr.decode()}")
    
    @staticmethod
    def get_audio_duration(audio_path: str) -> float:
        """
        Get duration of audio file in seconds
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Duration in seconds
        """
        try:
            probe = ffmpeg.probe(audio_path)
            duration = float(probe['streams'][0]['duration'])
            return duration
        except (ffmpeg.Error, KeyError, ValueError) as e:
            raise Exception(f"Error getting audio duration: {str(e)}")
