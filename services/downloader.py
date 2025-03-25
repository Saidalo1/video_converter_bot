"""
Video download service.
Handles downloading videos from URLs and saving Telegram files.
"""
import os
from pathlib import Path
from typing import Optional
import aiohttp
import asyncio
import json

import yt_dlp
from aiogram import Bot
from aiogram.types import File as TelegramFile
from aiogram.exceptions import TelegramBadRequest

from utils.config import config
from utils.logger import logger


class VideoDownloader:
    """
    Service for downloading videos from URLs or saving Telegram files.
    """
    
    def __init__(self):
        self.temp_dir = config.TEMP_DIR
        self.max_file_size_mb = config.MAX_FILE_SIZE_MB
        self.chunk_size = 1024 * 1024  # 1MB chunks
    
    async def download_from_telegram(self, bot: Bot, file_id: str, user_id: Optional[int] = None) -> Optional[Path]:
        """
        Download a file from Telegram.
        
        Args:
            bot: Aiogram Bot instance
            file_id: Telegram file ID
            user_id: User ID for admin check
            
        Returns:
            Path to downloaded file or None if download failed
        """
        try:
            # Generate a unique filename
            file_path = self.temp_dir / f"download_{os.urandom(4).hex()}.mp4"
            
            # Get file info using local Bot API server
            bot_token = bot.token
            async with aiohttp.ClientSession() as session:
                # Get file info
                url = f"{config.TELEGRAM_API_URL}/bot{bot_token}/getFile"
                params = {'file_id': file_id}
                
                logger.info(f"Getting file info from: {url}")
                logger.info(f"Request params: {params}")
                
                async with session.get(url, params=params) as response:
                    response_text = await response.text()
                    logger.info(f"Response status: {response.status}")
                    logger.info(f"Response headers: {response.headers}")
                    logger.info(f"Response body: {response_text}")
                    
                    if response.status != 200:
                        logger.error(f"Error getting file info: {response.status}")
                        logger.error(f"Response headers: {response.headers}")
                        return None
                    
                    try:
                        result = json.loads(response_text)
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse JSON response: {e}")
                        logger.error(f"Raw response: {response_text}")
                        return None
                    
                    if not result.get('ok'):
                        logger.error(f"Error getting file info: {result.get('description')}")
                        return None
                    
                    file_path_str = result['result']['file_path']
                    if not file_path_str:
                        logger.error("File path is empty")
                        return None
                    
                    logger.info(f"Got file path: {file_path_str}")
                    
                    # Копируем файл напрямую из примонтированной директории
                    source_path = Path(file_path_str)
                    if source_path.exists():
                        import shutil
                        shutil.copy2(source_path, file_path)
                        logger.info(f"Successfully copied file from {source_path} to {file_path}")
                        return file_path
                    
                    # Если файл недоступен напрямую, пробуем скачать через API
                    logger.info("File not accessible directly, trying to download through API")
                    
                    # Получаем относительный путь для API
                    api_path = file_path_str
                    if api_path.startswith('/var/lib/telegram-bot-api/'):
                        # Убираем базовый путь и токен бота
                        parts = api_path.split('/')
                        if len(parts) > 4:  # ['', 'var', 'lib', 'telegram-bot-api', 'BOT_TOKEN', ...]
                            api_path = '/'.join(parts[5:])  # Берем только части после токена бота
                    
                    logger.info(f"Using API path: {api_path}")
                
                # Download file in chunks
                offset = 0
                with open(file_path, 'wb') as f:
                    while True:
                        url = f"{config.TELEGRAM_API_URL}/file/bot{bot_token}/{api_path}"
                        headers = {'Range': f'bytes={offset}-{offset + self.chunk_size - 1}'}
                        
                        logger.info(f"Downloading chunk from: {url}")
                        logger.info(f"Request headers: {headers}")
                        
                        async with session.get(url, headers=headers) as response:
                            response_headers = dict(response.headers)
                            logger.info(f"Download response status: {response.status}")
                            logger.info(f"Download response headers: {response_headers}")
                            
                            if response.status == 416:  # Range Not Satisfiable
                                break
                            
                            if response.status != 206 and response.status != 200:  # Partial Content или полный файл
                                response_text = await response.text()
                                logger.error(f"Error downloading chunk: {response.status}")
                                logger.error(f"Response headers: {response.headers}")
                                logger.error(f"Response body: {response_text}")
                                return None
                            
                            chunk = await response.read()
                            if not chunk:
                                break
                            
                            chunk_size = len(chunk)
                            logger.info(f"Received chunk size: {chunk_size} bytes")
                            
                            f.write(chunk)
                            offset += chunk_size
                            
                            # Log progress
                            if offset % (5 * 1024 * 1024) == 0:  # Log every 5MB
                                logger.info(f"Downloaded {offset / (1024 * 1024):.1f} MB")
                            
                            # Если получили весь файл сразу (не частями)
                            if response.status == 200:
                                break
            
            logger.info(f"Successfully downloaded file in chunks: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error downloading file from Telegram: {str(e)}")
            logger.exception("Full traceback:")
            return None
    
    def download_from_url(self, url: str, user_id: Optional[int] = None) -> Optional[Path]:
        """
        Download a video from a URL using yt-dlp.
        
        Args:
            url: URL to download from
            user_id: User ID for admin check
            
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
                
                # Check if file exists and size is within limits (skip for admins)
                if not downloaded_file.exists():
                    logger.error(f"Downloaded file does not exist: {downloaded_file}")
                    return None
                
                file_size_mb = downloaded_file.stat().st_size / (1024 * 1024)
                if user_id not in config.ADMIN_USER_IDS and file_size_mb > self.max_file_size_mb:
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
