"""
Handlers package initialization.
Import and register all handlers here.
"""
from aiogram import Router
from .commands import register_command_handlers
from .video_handlers import register_video_handlers


def register_handlers(router: Router) -> None:
    """
    Register all handlers.
    
    Args:
        router: Router instance to register handlers to
    """
    register_command_handlers(router)
    register_video_handlers(router)
