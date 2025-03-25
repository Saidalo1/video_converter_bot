"""
Video download service.
Handles downloading videos from URLs and saving Telegram files.
"""
import os
from pathlib import Path
from typing import Optional

import yt_dlp
from aiogram import Bot
from aiogram.types import File as TelegramFile

from utils.config import config
from utils.logger import logger


class VideoDownloader:
    """
    Service for downloading videos from URLs or saving Telegram files.
    """
    
    def __init__(self):
        self.temp_dir = config.TEMP_DIR
        self.max_file_size_mb = config.MAX_FILE_SIZE_MB
    
    async def download_from_telegram(self, bot: Bot, file_id: str) -> Optional[Path]:
        """
        Download a file from Telegram.
        
        Args:
            bot: Aiogram Bot instance
            file_id: Telegram file ID
            
        Returns:
            Path to downloaded file or None if download failed
        """
        try:
            # Get file info
            file: TelegramFile = await bot.get_file(file_id)
            
            # Check file size
            if file.file_size > self.max_file_size_mb * 1024 * 1024:
                logger.warning(f"File size exceeds limit: {file.file_size / (1024 * 1024):.2f} MB")
                return None
            
            # Generate a unique filename based on file_unique_id
            file_path = self.temp_dir / f"{file.file_unique_id}{Path(file.file_path).suffix}"
            
            # Download the file
            await bot.download_file(file.file_path, destination=file_path)
            logger.info(f"Downloaded file from Telegram: {file_path}")
            
            return file_path
        except Exception as e:
            logger.error(f"Error downloading file from Telegram: {str(e)}")
            return None
    
    def download_from_url(self, url: str) -> Optional[Path]:
        """
        Download a video from a URL using yt-dlp.
        
        Args:
            url: URL to download from
            
        Returns:
            Path to downloaded file or None if download failed
        """
        try:
            # Generate a temp filename
            temp_filename = os.path.join(self.temp_dir, f"download_{os.urandom(4).hex()}.mp4")
            
            # Configure yt-dlp options
            ydl_opts = {
                'format': 'best[ext=mp4]/best',  # Prefer MP4 format
                'outtmpl': temp_filename,
                'noplaylist': True,
                'quiet': True,
                'no_warnings': True,
                'restrictfilenames': True,
            }
            
            # Download the video
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                downloaded_file = Path(ydl.prepare_filename(info))
                
                # Check if file exists and size is within limits
                if not downloaded_file.exists():
                    logger.error(f"Downloaded file does not exist: {downloaded_file}")
                    return None
                
                file_size_mb = downloaded_file.stat().st_size / (1024 * 1024)
                if file_size_mb > self.max_file_size_mb:
                    logger.warning(f"Downloaded file exceeds size limit: {file_size_mb:.2f} MB")
                    os.remove(downloaded_file)
                    return None
                
                logger.info(f"Downloaded video from URL: {url} -> {downloaded_file}")
                return downloaded_file
        except Exception as e:
            logger.error(f"Error downloading from URL {url}: {str(e)}")
            return None


# Create a global instance
video_downloader = VideoDownloader()
