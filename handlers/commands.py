"""
Command handlers for the Telegram bot.
Handles user commands like /start, /help, etc.
"""
from typing import Union
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from utils.logger import logger
from utils.rate_limiter import rate_limiter
from utils.localization import get_text, user_language, LANGUAGES
from services.downloader import video_downloader


# Create router for command handlers
router = Router()


def register_command_handlers(main_router: Router) -> None:
    """
    Register command handlers with the main router.
    
    Args:
        main_router: Main router instance to include command handlers
    """
    main_router.include_router(router)


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    """
    Handler for the /start command.
    
    Args:
        message: Incoming message object
    """
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    lang = user_language.get_user_language(user_id)
    
    logger.info(f"User {user_id} ({username}) started the bot")
    
    # Создаем клавиатуру с основными командами в виде reply кнопок
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📹 Конвертировать"), KeyboardButton(text="💽 Сжать")],
            [KeyboardButton(text="🎧 Извлечь аудио"), KeyboardButton(text="✂️ Обрезать")],
            [KeyboardButton(text="⚙️ Настройки"), KeyboardButton(text="❓ Помощь")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Отправьте видео или ссылку на видео"
    )
    
    greeting = get_text("start", "greeting", lang, username=username)
    
    await message.answer(greeting, reply_markup=keyboard, parse_mode="HTML")


@router.message(Command("help"))
@router.callback_query(F.data == "help")
@router.message(F.text == "❓ Помощь")
async def cmd_help(event: Union[Message, CallbackQuery]) -> None:
    """
    Handler for the /help command and help button.
    
    Args:
        event: Incoming message or callback query
    """
    if isinstance(event, CallbackQuery):
        message = event.message
        user_id = event.from_user.id
        await event.answer()  # Отвечаем на callback query, чтобы убрать часы загрузки
    else:
        message = event
        user_id = message.from_user.id
    
    lang = user_language.get_user_language(user_id)
    
    is_allowed, _ = rate_limiter.check_rate_limit(user_id)
    if not is_allowed:
        await message.answer(get_text("errors", "rate_limit_exceeded", lang))
        return
    
    # Создаем список команд с локализованными описаниями
    commands_list = (
        "/start - " + get_text("command_descriptions", "start", lang) + "\n" +
        "/help - " + get_text("command_descriptions", "help", lang) + "\n" +
        "/convert - " + get_text("command_descriptions", "convert", lang) + "\n" +
        "/compress - " + get_text("command_descriptions", "compress", lang) + "\n" +
        "/extract_audio - " + get_text("command_descriptions", "extract_audio", lang) + "\n" +
        "/trim - " + get_text("command_descriptions", "trim", lang) + "\n" +
        "/cancel - " + get_text("command_descriptions", "cancel", lang) + "\n" +
        "/settings - " + get_text("command_descriptions", "settings", lang) + "\n"
    )
    
    # Формируем текст справки
    help_text = (
        f"📋 <b>{get_text('help', 'title', lang)}</b>\n\n" +
        commands_list + "\n" +
        f"<b>{get_text('help', 'how_to_use', lang)}</b>\n" +
        f"{get_text('help', 'how_to_use_steps', lang)}\n\n" +
        f"<b>{get_text('help', 'limitations', lang)}</b>\n" +
        f"{get_text('help', 'max_file_size', lang, max_file_size=video_downloader.max_file_size_mb)}\n" +
        f"{get_text('help', 'max_requests', lang, max_requests=rate_limiter._max_requests)}\n"
    )
    
    if isinstance(event, CallbackQuery):
        # Для callback используем inline кнопку для возврата
        kb = InlineKeyboardBuilder()
        kb.button(text="◀️ Назад", callback_data="back_to_start")
        await message.edit_text(help_text, reply_markup=kb.as_markup(), parse_mode="HTML")
    else:
        await message.answer(help_text, parse_mode="HTML")


@router.message(Command("settings"))
@router.callback_query(F.data == "settings")
@router.message(F.text == "⚙️ Настройки")
async def cmd_settings(event: Message | CallbackQuery) -> None:
    """
    Handler for the /settings command and settings button.
    
    Args:
        event: Incoming message or callback query
    """
    if isinstance(event, CallbackQuery):
        message = event.message
        user_id = event.from_user.id
        await event.answer()
    else:
        message = event
        user_id = message.from_user.id
    
    lang = user_language.get_user_language(user_id)
    
    # Создаем клавиатуру с кнопками настроек
    kb = InlineKeyboardBuilder()
    kb.button(
        text=get_text("settings", "change_language", lang),
        callback_data="change_language"
    )
    kb.button(text=get_text("command_descriptions", "help", lang), callback_data="help")
    kb.adjust(1)  # По одной кнопке в ряд
    
    settings_text = (
        f"<b>{get_text('settings', 'title', lang)}</b>\n\n" +
        f"{get_text('settings', 'language', lang, current_language=LANGUAGES[lang])}"
    )
    
    if isinstance(event, CallbackQuery):
        await message.edit_text(settings_text, reply_markup=kb.as_markup(), parse_mode="HTML")
    else:
        await message.answer(settings_text, reply_markup=kb.as_markup(), parse_mode="HTML")


@router.callback_query(F.data == "change_language")
async def cmd_change_language(callback: CallbackQuery) -> None:
    """
    Handler for the change language button.
    
    Args:
        callback: Callback query
    """
    user_id = callback.from_user.id
    lang = user_language.get_user_language(user_id)
    
    # Создаем клавиатуру с кнопками выбора языка
    kb = InlineKeyboardBuilder()
    for lang_code, lang_name in LANGUAGES.items():
        kb.button(text=lang_name, callback_data=f"set_lang_{lang_code}")
    kb.button(text="↩️", callback_data="settings")
    kb.adjust(1)  # По одной кнопке в ряд
    
    await callback.answer()
    await callback.message.edit_text(
        get_text("language_selection", "title", lang),
        reply_markup=kb.as_markup()
    )


@router.callback_query(F.data.startswith("set_lang_"))
async def cmd_set_language(callback: CallbackQuery) -> None:
    """
    Handler for language selection.
    
    Args:
        callback: Callback query
    """
    user_id = callback.from_user.id
    lang_code = callback.data.split("_")[-1]
    
    # Устанавливаем выбранный язык
    user_language.set_user_language(user_id, lang_code)
    lang = user_language.get_user_language(user_id)
    
    await callback.answer()
    
    # Отправляем сообщение о смене языка
    await callback.message.edit_text(
        get_text("language_selection", "language_changed", lang),
        reply_markup=InlineKeyboardBuilder().button(
            text=get_text("command_descriptions", "settings", lang),
            callback_data="settings"
        ).as_markup()
    )


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    """
    Handler for the /cancel command.
    Cancels any ongoing operation and resets user state.
    
    Args:
        message: Incoming message object
        state: FSM context for the user
    """
    current_state = await state.get_state()
    
    user_id = message.from_user.id
    lang = user_language.get_user_language(user_id)
    
    if current_state is None:
        await message.answer(get_text("errors", "no_active_operation", lang))
        return
    
    # Reset state
    await state.clear()
    
    # Отправляем сообщение об отмене операции
    await message.answer(get_text("errors", "operation_canceled", lang))
    
    logger.info(f"User {message.from_user.id} canceled operation in state {current_state}")


@router.message(Command("admin"))
async def cmd_admin(message: Message) -> None:
    """
    Handler for the /admin command.
    Only accessible to admin users.
    
    Args:
        message: Incoming message object
    """
    from utils.config import config
    
    user_id = message.from_user.id
    
    if user_id not in config.ADMIN_USER_IDS:
        logger.warning(f"Unauthorized admin access attempt by user {user_id}")
        await message.answer("❌ У вас нет доступа к этой команде.")
        return
    
    admin_text = (
        "🔑 <b>Панель администратора</b>\n\n"
        "/stats - Показать статистику использования бота\n"
        "/block_user [user_id] - Заблокировать пользователя\n"
        "/unblock_user [user_id] - Разблокировать пользователя\n"
    )
    
    await message.answer(admin_text, parse_mode="HTML")
