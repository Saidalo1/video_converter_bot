"""
Telegram Video Converter Bot
Main entry point for the bot application.
"""
import asyncio
import os
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from utils.config import config
from utils.logger import logger
from utils.localization import get_text
from handlers import commands, video_handlers


async def register_commands(bot: Bot) -> None:
    """
    Register bot commands for display in Telegram UI.
    
    Args:
        bot: Bot instance
    """
    # Регистрируем команды для разных языков
    for lang_code in ["ru", "en", "uz"]:
        commands_list = [
            BotCommand(command="start", description=get_text("command_descriptions", "start", lang_code)),
            BotCommand(command="help", description=get_text("command_descriptions", "help", lang_code)),
            BotCommand(command="convert", description=get_text("command_descriptions", "convert", lang_code)),
            BotCommand(command="compress", description=get_text("command_descriptions", "compress", lang_code)),
            BotCommand(command="extract_audio", description=get_text("command_descriptions", "extract_audio", lang_code)),
            BotCommand(command="trim", description=get_text("command_descriptions", "trim", lang_code)),
            BotCommand(command="cancel", description=get_text("command_descriptions", "cancel", lang_code)),
            BotCommand(command="settings", description=get_text("command_descriptions", "settings", lang_code)),
        ]
        
        # Устанавливаем команды для конкретного языка
        await bot.set_my_commands(commands_list, language_code=lang_code)
    
    # Устанавливаем команды по умолчанию (русский)
    default_commands = [
        BotCommand(command="start", description=get_text("command_descriptions", "start", "ru")),
        BotCommand(command="help", description=get_text("command_descriptions", "help", "ru")),
        BotCommand(command="convert", description=get_text("command_descriptions", "convert", "ru")),
        BotCommand(command="compress", description=get_text("command_descriptions", "compress", "ru")),
        BotCommand(command="extract_audio", description=get_text("command_descriptions", "extract_audio", "ru")),
        BotCommand(command="trim", description=get_text("command_descriptions", "trim", "ru")),
        BotCommand(command="cancel", description=get_text("command_descriptions", "cancel", "ru")),
        BotCommand(command="settings", description=get_text("command_descriptions", "settings", "ru")),
    ]
    await bot.set_my_commands(default_commands)
    
    logger.info("Bot commands registered")


async def main() -> None:
    """
    Main entry point for the bot.
    Initialize bot, register handlers and start polling.
    """
    # Check if the bot token is set
    if not config.BOT_TOKEN:
        logger.error("BOT_TOKEN is not set in .env file")
        sys.exit(1)
    
    # Initialize bot and dispatcher
    bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Register handlers
    dp.include_router(commands.router)
    dp.include_router(video_handlers.router)
    
    # Register commands
    await register_commands(bot)
    
    # Create temporary directory if not exists
    os.makedirs(config.TEMP_DIR, exist_ok=True)
    
    # Start polling
    logger.info("Starting bot...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
