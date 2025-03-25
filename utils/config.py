"""
Configuration module for the video converter bot.
Loads and validates environment variables.
"""
import os
import logging
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv
from pydantic import BaseModel, field_validator

# Load environment variables from .env file
load_dotenv()

# Обработка ADMIN_USER_IDS из переменной окружения
admin_ids_str = os.getenv("ADMIN_USER_IDS", "")
admin_ids = []
if admin_ids_str:
    try:
        admin_ids = [int(user_id.strip()) for user_id in admin_ids_str.split(",") if user_id.strip()]
    except ValueError:
        logging.error(f"Неверный формат ADMIN_USER_IDS: {admin_ids_str}")


class Config(BaseModel):
    """Bot configuration settings loaded from environment variables."""
    
    # Bot settings
    BOT_TOKEN: str
    
    # FFmpeg settings
    FFMPEG_PATH: str = "/usr/bin/ffmpeg"
    
    # Rate limiting
    MAX_REQUESTS_PER_MINUTE: int = 5
    MAX_FILE_SIZE_MB: int = 50
    
    # Admin configuration
    ADMIN_USER_IDS: List[int] = admin_ids
    
    # File storage
    TEMP_DIR: Path = Path("./temp")
    
    # Валидатор для ADMIN_USER_IDS больше не используется, так как мы обрабатываем
    # значение перед созданием экземпляра Config
    
    @field_validator("TEMP_DIR", mode="after")
    @classmethod
    def create_temp_dir(cls, v: Path) -> Path:
        """Ensure the temporary directory exists."""
        v.mkdir(parents=True, exist_ok=True)
        return v


# Обработка строки с ID администраторов
admin_ids_str = os.getenv("ADMIN_USER_IDS", "")
admin_ids = []
if admin_ids_str:
    try:
        admin_ids = [int(user_id.strip()) for user_id in admin_ids_str.split(",") if user_id.strip()]
    except ValueError:
        logging.error(f"Неверный формат ADMIN_USER_IDS: {admin_ids_str}")

# Create a global config instance
config = Config(
    BOT_TOKEN=os.getenv("BOT_TOKEN", ""),
    FFMPEG_PATH=os.getenv("FFMPEG_PATH", "/usr/bin/ffmpeg"),
    MAX_REQUESTS_PER_MINUTE=int(os.getenv("MAX_REQUESTS_PER_MINUTE", 5)),
    MAX_FILE_SIZE_MB=int(os.getenv("MAX_FILE_SIZE_MB", 50)),
    ADMIN_USER_IDS=admin_ids,
    TEMP_DIR=Path(os.getenv("TEMP_DIR", "./temp")),
)
