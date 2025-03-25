"""
Configuration management.
Loads environment variables and provides configuration values.
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
    """Configuration class that loads and validates environment variables."""
    
    def __init__(self, **data):
        super().__init__(**data)
        # Create temp directory if it doesn't exist
        os.makedirs(self.TEMP_DIR, exist_ok=True)

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
    
    # Telegram API credentials
    API_ID: Optional[str] = None
    API_HASH: Optional[str] = None
    
    # Telegram API URL (for local Bot API server)
    TELEGRAM_API_URL: str = "https://api.telegram.org"
    
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
    API_ID=os.getenv("API_ID"),
    API_HASH=os.getenv("API_HASH"),
    RATE_LIMIT_REQUESTS=int(os.getenv("RATE_LIMIT_REQUESTS", 5)),
    RATE_LIMIT_PERIOD=int(os.getenv("RATE_LIMIT_PERIOD", 60)),
    TELEGRAM_API_URL=os.getenv("TELEGRAM_API_URL", "https://api.telegram.org"),
)
