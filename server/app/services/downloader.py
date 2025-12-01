"""
YouTube Video Downloader Service
Uses yt-dlp to download videos and extract metadata
"""

import os
import yt_dlp
from typing import Dict, Any
from app.core.config import settings


class YouTubeDownloader:
    """Service for downloading YouTube videos using yt-dlp"""
    
    def __init__(self, temp_dir: str = None):
        self.temp_dir = temp_dir or settings.TEMP_DIR
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def get_video_info(self, url: str) -> Dict[str, Any]:
        """
        Extract video metadata without downloading
        
        Args:
            url: YouTube video URL
            
        Returns:
            Dictionary with video metadata
        """
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            # Anti-blocking measures
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web'],
                    'skip': ['hls', 'dash']
                }
            },
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            return {
                'id': info.get('id'),
                'title': info.get('title'),
                'duration': info.get('duration'),
                'uploader': info.get('uploader'),
                'upload_date': info.get('upload_date'),
                'view_count': info.get('view_count'),
                'thumbnail': info.get('thumbnail'),
                'description': info.get('description', '')[:500],  # First 500 chars
            }
    
    def download_video(self, url: str, output_filename: str = None) -> str:
        """
        Download YouTube video
        
        Args:
            url: YouTube video URL
            output_filename: Optional custom filename
            
        Returns:
            Path to downloaded video file
        """
        if output_filename is None:
            output_filename = '%(id)s.%(ext)s'
        
        output_path = os.path.join(self.temp_dir, output_filename)
        
        ydl_opts = {
            'format': 'best[ext=mp4]/best',  # Prefer mp4
            'outtmpl': output_path,
            'quiet': True,
            'no_warnings': True,
            # Anti-blocking measures
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web'],
                    'skip': ['hls', 'dash']
                }
            },
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            # Get actual filename after download
            filename = ydl.prepare_filename(info)
            
        return filename
    
    def download_audio_only(self, url: str, output_filename: str = None) -> str:
        """
        Download only audio from YouTube video (faster and smaller)
        
        Args:
            url: YouTube video URL
            output_filename: Optional custom filename
            
        Returns:
            Path to downloaded audio file
        """
        if output_filename is None:
            output_filename = '%(id)s.%(ext)s'
        
        output_path = os.path.join(self.temp_dir, output_filename)
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_path,
            'quiet': True,
            'no_warnings': True,
            # Anti-blocking measures
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web'],
                    'skip': ['hls', 'dash']
                }
            },
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            # Audio file will have .mp3 extension after post-processing
            video_id = info.get('id')
            audio_filename = os.path.join(self.temp_dir, f"{video_id}.mp3")
            
        return audio_filename
