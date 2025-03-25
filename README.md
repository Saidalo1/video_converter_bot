# Telegram Video Converter Bot

This is a Telegram bot that allows users to process video files. The bot is built using Python, Aiogram, and FFmpeg.

## Features

- **Format Conversion**: Convert videos to different formats (MP4, MKV, AVI, MOV, GIF)
- **Video Compression**: Compress videos with adjustable quality settings
- **Audio Extraction**: Extract audio from videos in various formats (MP3, WAV, AAC)
- **Video Trimming**: Cut videos to specific time ranges
- **URL Support**: Process videos from URLs (YouTube, Vimeo, etc.)
- **Spam Protection**: Rate limiting and file size restrictions
- **Admin Features**: Tools for managing users and monitoring usage

## Tech Stack

- **Language**: Python 3.8+
- **Framework**: Aiogram 3.x
- **Video Processing**: FFmpeg (via ffmpeg-python)
- **URL Download**: yt-dlp
- **State Management**: FSM with MemoryStorage
- **Configuration**: Environment variables with python-dotenv
- **Containerization**: Docker & Docker Compose

## Project Structure

```
video_converter_bot/
├── bot.py                 # Main entry point
├── .env                   # Environment variables
├── requirements.txt       # Dependencies
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose configuration
├── handlers/              # Telegram message handlers
│   ├── commands.py        # Command handlers
│   └── video_handlers.py  # Video processing handlers
├── services/              # Business logic
│   ├── downloader.py      # Video download service
│   └── video_processor.py # Video processing service
└── utils/                 # Utilities
    ├── config.py          # Configuration
    ├── logger.py          # Logging
    └── rate_limiter.py    # Rate limiting
```

## Installation

### Using Docker (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd video_converter_bot
```

2. Configure environment variables in `.env` file:
```
BOT_TOKEN=your_telegram_bot_token
FFMPEG_PATH=/usr/bin/ffmpeg
MAX_REQUESTS_PER_MINUTE=5
MAX_FILE_SIZE_MB=50
ADMIN_USER_IDS=123456789,987654321
TEMP_DIR=./temp
```

3. Build and start the bot using Docker Compose:
```bash
docker-compose up -d --build
```

4. View logs:
```bash
docker-compose logs -f
```

5. Stop the bot:
```bash
docker-compose down
```

### Manual Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd video_converter_bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install FFmpeg:
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install ffmpeg

# CentOS/RHEL
sudo yum install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

4. Configure environment variables in `.env` file:
```
BOT_TOKEN=your_telegram_bot_token
FFMPEG_PATH=/path/to/ffmpeg
MAX_REQUESTS_PER_MINUTE=5
MAX_FILE_SIZE_MB=50
ADMIN_USER_IDS=123456789,987654321
TEMP_DIR=./temp
```

5. Start the bot:
```bash
python bot.py
```

## Usage

1. Open Telegram and start a conversation with your bot.

2. Send a video file or a URL to a video.

3. Follow the bot's instructions to process the video.

## Future Enhancements

- Cloud storage integration (AWS S3, Google Cloud Storage)
- Web dashboard for usage statistics
- AI-powered video enhancements
- Premium features for subscribers
- Database integration for user management and analytics

## License

[MIT License](LICENSE)
