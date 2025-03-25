"""
Main entry point for the video converter bot.
"""
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from handlers import register_handlers
from utils.config import config
from utils.logger import logger


async def main():
    """Main entry point for the bot."""
    # Initialize bot and dispatcher
    bot = Bot(token=config.BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()
    
    # Register handlers
    register_handlers(dp)
    
    # Register bot commands
    await bot.set_my_commands([
        BotCommand(command="start", description="Start the bot"),
        BotCommand(command="help", description="Show help message"),
        BotCommand(command="settings", description="Configure bot settings"),
    ])
    
    logger.info("Bot commands registered")
    
    # Start polling
    logger.info("Starting bot...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main()) 