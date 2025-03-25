"""
Video processing handlers for the Telegram bot.
Handles video uploads, URL processing, and processing operations.
"""
import re
from pathlib import Path
from typing import Optional, Union

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, FSInputFile
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.exceptions import TelegramBadRequest

from utils.logger import logger
from utils.rate_limiter import rate_limiter
from utils.localization import get_i18n_for_user
from services.downloader import video_downloader
from services.video_processor import video_processor


# Create router for video handlers
router = Router()


# Define states for conversation flow
class VideoProcessingStates(StatesGroup):
    """FSM states for video processing workflow."""
    waiting_for_video = State()
    waiting_for_operation = State()
    waiting_for_format = State()
    waiting_for_quality = State()
    waiting_for_audio_format = State()
    waiting_for_audio_bitrate = State()
    waiting_for_trim_start = State()
    waiting_for_trim_end = State()
    processing = State()


# Helper function to validate URLs
def is_valid_video_url(url: str) -> bool:
    """
    Check if the URL is a valid video URL.
    
    Args:
        url: URL to check
        
    Returns:
        True if the URL is valid, False otherwise
    """
    # Basic URL validation
    url_pattern = re.compile(
        r'^(https?://)?(www\.)?(youtube\.com|youtu\.be|vimeo\.com|dailymotion\.com|facebook\.com|instagram\.com)/.*'
    )
    return bool(url_pattern.match(url))


@router.message(F.video)
async def handle_video_upload(message: Message, state: FSMContext) -> None:
    """
    Handler for video file uploads.
    
    Args:
        message: Incoming message with video
        state: FSM context for the user
    """
    user_id = message.from_user.id
    
    # Check rate limiting
    is_allowed, requests_remaining = rate_limiter.check_rate_limit(user_id)
    if not is_allowed:
        await message.answer(
            "⚠️ Превышен лимит запросов. Пожалуйста, попробуйте позже."
        )
        return
    
    # Tell user we're processing their video
    processing_msg = await message.answer("⏳ Получаю видео...")
    
    try:
        # Download the video
        video_file = await video_downloader.download_from_telegram(
            message.bot, message.video.file_id
        )
        
        if not video_file:
            await message.answer(
                "❌ Не удалось загрузить видео. "
                f"Убедитесь, что размер файла не превышает {video_downloader.max_file_size_mb} МБ."
            )
            return
        
        # Store file path in state
        await state.update_data(video_path=str(video_file))
        
        # Show operation options
        await show_operation_options(message, processing_msg.message_id)
        
        # Update state
        await state.set_state(VideoProcessingStates.waiting_for_operation)
        
    except Exception as e:
        logger.error(f"Error handling video upload: {str(e)}")
        await message.answer("❌ Произошла ошибка при обработке видео.")
        await state.clear()


@router.message(F.text.regexp(r'https?://'))
async def handle_video_url(message: Message, state: FSMContext) -> None:
    """
    Handler for video URLs.
    
    Args:
        message: Incoming message with URL
        state: FSM context for the user
    """
    url = message.text.strip()
    user_id = message.from_user.id
    
    # Check if URL is valid
    if not is_valid_video_url(url):
        await message.answer(
            "❌ Неверный формат URL. Пожалуйста, отправьте корректную ссылку на видео."
        )
        return
    
    # Check rate limiting
    is_allowed, requests_remaining = rate_limiter.check_rate_limit(user_id)
    if not is_allowed:
        await message.answer(
            "⚠️ Превышен лимит запросов. Пожалуйста, попробуйте позже."
        )
        return
    
    # Tell user we're processing their URL
    processing_msg = await message.answer("⏳ Загружаю видео по ссылке...")
    
    try:
        # Download the video
        video_file = video_downloader.download_from_url(url)
        
        if not video_file:
            await message.answer(
                "❌ Не удалось загрузить видео по ссылке. "
                "Проверьте ссылку или попробуйте другое видео."
            )
            return
        
        # Store file path in state
        await state.update_data(video_path=str(video_file))
        
        # Show operation options
        await show_operation_options(message, processing_msg.message_id)
        
        # Update state
        await state.set_state(VideoProcessingStates.waiting_for_operation)
        
    except Exception as e:
        logger.error(f"Error handling video URL: {str(e)}")
        await message.answer("❌ Произошла ошибка при загрузке видео по ссылке.")
        await state.clear()


async def show_operation_options(message: Message, reply_to_message_id: Optional[int] = None) -> None:
    """
    Show available video processing operations.
    
    Args:
        message: Message to reply to
        reply_to_message_id: Optional message ID to edit instead of sending new message
    """
    # Create inline keyboard with operation options
    kb = InlineKeyboardBuilder()
    kb.button(text="🔄 Конвертировать", callback_data="operation:convert")
    kb.button(text="🗜️ Сжать", callback_data="operation:compress")
    kb.button(text="🔊 Извлечь аудио", callback_data="operation:extract_audio")
    kb.button(text="✂️ Обрезать", callback_data="operation:trim")
    kb.adjust(2)
    
    if reply_to_message_id:
        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=reply_to_message_id,
            text="🎬 Выберите операцию, которую нужно выполнить с видео:",
            reply_markup=kb.as_markup()
        )
    else:
        await message.answer(
            "🎬 Выберите операцию, которую нужно выполнить с видео:",
            reply_markup=kb.as_markup()
        )


@router.callback_query(F.data.startswith("operation:"))
async def process_operation_selection(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Process operation selection from inline keyboard.
    
    Args:
        callback: Callback query
        state: FSM context for the user
    """
    # Extract the selected operation
    operation = callback.data.split(":")[1]
    
    # Store the operation in state
    await state.update_data(operation=operation)
    
    # Handle different operations
    if operation == "convert":
        await handle_convert_operation(callback, state)
    elif operation == "compress":
        await handle_compress_operation(callback, state)
    elif operation == "extract_audio":
        await handle_extract_audio_operation(callback, state)
    elif operation == "trim":
        await handle_trim_operation(callback, state)
    
    # Answer the callback query to remove the loading indicator
    await callback.answer()


async def handle_convert_operation(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Handle conversion operation.
    
    Args:
        callback: Callback query
        state: FSM context for the user
    """
    # Получаем локализацию
    i18n = await get_i18n_for_user(callback.from_user.id)
    
    # Create format selection keyboard
    kb = InlineKeyboardBuilder()
    kb.button(text="MP4", callback_data="format:mp4")
    kb.button(text="MKV", callback_data="format:mkv")
    kb.button(text="AVI", callback_data="format:avi")
    kb.button(text="MOV", callback_data="format:mov")
    kb.button(text="WebM", callback_data="format:webm")
    kb.button(text="GIF", callback_data="format:gif")
    kb.button(text=i18n["common"]["back"], callback_data="operation:back")
    kb.button(text=i18n["common"]["cancel"], callback_data="format:cancel")
    kb.adjust(3)
    
    # Update message with format selection
    await callback.message.edit_text(
        "🔄 Выберите формат для конвертации:",
        reply_markup=kb.as_markup()
    )
    
    # Update state
    await state.set_state(VideoProcessingStates.waiting_for_format)


async def handle_compress_operation(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Handle compression operation.
    
    Args:
        callback: Callback query
        state: FSM context for the user
    """
    # Получаем локализацию
    i18n = await get_i18n_for_user(callback.from_user.id)
    
    # Create quality selection keyboard
    kb = InlineKeyboardBuilder()
    kb.button(text=i18n["compress_operation"]["high_quality"], callback_data="quality:high")
    kb.button(text=i18n["compress_operation"]["medium_quality"], callback_data="quality:medium")
    kb.button(text=i18n["compress_operation"]["low_quality"], callback_data="quality:low")
    kb.button(text=i18n["common"]["back"], callback_data="operation:back")
    kb.button(text=i18n["common"]["cancel"], callback_data="quality:cancel")
    kb.adjust(2)
    
    # Update message with quality selection
    await callback.message.edit_text(
        "🗜️ Выберите качество сжатия:",
        reply_markup=kb.as_markup()
    )
    
    # Update state
    await state.set_state(VideoProcessingStates.waiting_for_quality)


async def handle_extract_audio_operation(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Handle audio extraction operation.
    
    Args:
        callback: Callback query
        state: FSM context for the user
    """
    # Create audio format selection keyboard
    kb = InlineKeyboardBuilder()
    kb.button(text="MP3", callback_data="audio_format:mp3")
    kb.button(text="WAV", callback_data="audio_format:wav")
    kb.button(text="AAC", callback_data="audio_format:aac")
    kb.button(text="Отмена", callback_data="audio_format:cancel")
    kb.adjust(2)
    
    # Update message with audio format selection
    await callback.message.edit_text(
        "🔊 Выберите формат аудио:",
        reply_markup=kb.as_markup()
    )
    
    # Update state
    await state.set_state(VideoProcessingStates.waiting_for_audio_format)


async def handle_trim_operation(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Handle trim operation.
    
    Args:
        callback: Callback query
        state: FSM context for the user
    """
    # Update message with instructions
    await callback.message.edit_text(
        "✂️ Введите время начала отрезка (в секундах):"
    )
    
    # Update state
    await state.set_state(VideoProcessingStates.waiting_for_trim_start)


@router.callback_query(F.data.startswith("format:"), StateFilter(VideoProcessingStates.waiting_for_format))
async def process_format_selection(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Process format selection for conversion.
    
    Args:
        callback: Callback query
        state: FSM context for the user
    """
    # Extract the selected format
    format_value = callback.data.split(":")[1]
    
    # Проверяем действие пользователя
    if format_value == "cancel":
        i18n = await get_i18n_for_user(callback.from_user.id)
        await callback.message.edit_text(i18n["common"]["operation_canceled"])
        await state.clear()
        await callback.answer()
        return
    elif callback.data == "operation:back":
        # Возвращаемся к выбору операции
        await show_operation_options(callback.message, reply_to_message_id=callback.message.message_id)
        await callback.answer()
        return
    
    # Store the format in state
    await state.update_data(target_format=format_value)
    
    # Process the video
    # Добавляем очистку клавиатуры ответа
    await callback.message.edit_reply_markup(reply_markup=None)
    await process_video(callback.message, state)
    
    # Answer the callback query
    await callback.answer()


@router.callback_query(F.data.startswith("quality:"), StateFilter(VideoProcessingStates.waiting_for_quality))
async def process_quality_selection(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Process quality selection for compression.
    
    Args:
        callback: Callback query
        state: FSM context for the user
    """
    # Extract the selected quality
    quality = callback.data.split(":")[1]
    
    # Проверяем действие пользователя
    if quality == "cancel":
        i18n = await get_i18n_for_user(callback.from_user.id)
        await callback.message.edit_text(i18n["common"]["operation_canceled"])
        await state.clear()
        await callback.answer()
        return
    elif callback.data == "operation:back":
        # Возвращаемся к выбору операции
        await show_operation_options(callback.message, reply_to_message_id=callback.message.message_id)
        await callback.answer()
        return
    
    # Store the quality in state
    await state.update_data(quality=quality)
    
    # Process the video
    await process_video(callback.message, state)
    
    # Answer the callback query
    await callback.answer()


@router.callback_query(F.data.startswith("audio_format:"), StateFilter(VideoProcessingStates.waiting_for_audio_format))
async def process_audio_format_selection(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Process audio format selection for extraction.
    
    Args:
        callback: Callback query
        state: FSM context for the user
    """
    # Extract the selected audio format
    audio_format = callback.data.split(":")[1]
    
    # Проверяем действие пользователя
    if audio_format == "cancel":
        i18n = await get_i18n_for_user(callback.from_user.id)
        await callback.message.edit_text(i18n["common"]["operation_canceled"])
        await state.clear()
        await callback.answer()
        return
    elif callback.data == "operation:back":
        # Возвращаемся к выбору операции
        await show_operation_options(callback.message, reply_to_message_id=callback.message.message_id)
        await callback.answer()
        return
    
    # Store the audio format in state
    await state.update_data(audio_format=audio_format)
    
    # Create bitrate selection keyboard
    kb = InlineKeyboardBuilder()
    kb.button(text="Высокое (320k)", callback_data="bitrate:320k")
    kb.button(text="Среднее (192k)", callback_data="bitrate:192k")
    kb.button(text="Низкое (128k)", callback_data="bitrate:128k")
    kb.button(text="Отмена", callback_data="bitrate:cancel")
    kb.adjust(2)
    
    # Update message with bitrate selection
    await callback.message.edit_text(
        "🔊 Выберите битрейт аудио:",
        reply_markup=kb.as_markup()
    )
    
    # Update state
    await state.set_state(VideoProcessingStates.waiting_for_audio_bitrate)
    
    # Answer the callback query
    await callback.answer()


@router.callback_query(F.data.startswith("bitrate:"), StateFilter(VideoProcessingStates.waiting_for_audio_bitrate))
async def process_bitrate_selection(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Process bitrate selection for audio extraction.
    
    Args:
        callback: Callback query
        state: FSM context for the user
    """
    # Extract the selected bitrate
    bitrate = callback.data.split(":")[1]
    
    # Проверяем действие пользователя
    if bitrate == "cancel":
        i18n = await get_i18n_for_user(callback.from_user.id)
        await callback.message.edit_text(i18n["common"]["operation_canceled"])
        await state.clear()
        await callback.answer()
        return
    elif callback.data == "audio_format:back":
        # Возвращаемся к выбору формата аудио
        await handle_extract_audio_operation(callback, state)
        await callback.answer()
        return
    
    # Store the bitrate in state
    await state.update_data(bitrate=bitrate)
    
    # Process the video
    await process_video(callback.message, state)
    
    # Answer the callback query
    await callback.answer()


def parse_time_format(time_str: str) -> float:
    """
    Parse different time formats and convert to seconds.
    
    Supported formats:
    - Seconds (15)
    - MM:SS (01:15)
    - H:MM:SS (1:01:15)
    
    Returns:
        Time in seconds
    """
    # Clean spaces
    time_str = time_str.strip()
    
    # Try direct conversion to seconds
    try:
        return float(time_str)
    except ValueError:
        pass
    
    # Check MM:SS or H:MM:SS format
    parts = time_str.split(":")
    
    try:
        if len(parts) == 2:  # MM:SS
            minutes, seconds = parts
            return float(minutes) * 60 + float(seconds)
        elif len(parts) == 3:  # H:MM:SS
            hours, minutes, seconds = parts
            return float(hours) * 3600 + float(minutes) * 60 + float(seconds)
    except ValueError:
        pass
    
    # If no format matches
    raise ValueError("Invalid time format")


@router.message(StateFilter(VideoProcessingStates.waiting_for_trim_start))
async def process_trim_start(message: Message, state: FSMContext) -> None:
    """
    Process start time for trimming.
    
    Args:
        message: Message with start time
        state: FSM context for the user
    """
    try:
        # Try to parse different time formats
        start_time = parse_time_format(message.text)
        
        # Check if start time is valid
        if start_time < 0:
            i18n = await get_i18n_for_user(message.from_user.id)
            await message.answer(i18n["trim_operation"]["positive_time"])
            return
        
        # Store start time in state
        await state.update_data(trim_start=start_time)
        
        # Удаляем неиспользуемую клавиатуру
        
        # Get localization
        i18n = await get_i18n_for_user(message.from_user.id)
        
        # Create keyboard with localized buttons
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text=i18n["trim_operation"]["end_of_video"])],
                [KeyboardButton(text=i18n["trim_operation"]["preset_10_sec"]), 
                 KeyboardButton(text=i18n["trim_operation"]["preset_30_sec"]), 
                 KeyboardButton(text=i18n["trim_operation"]["preset_1_min"])],
                [KeyboardButton(text=i18n["trim_operation"]["preset_2_min"]), 
                 KeyboardButton(text=i18n["trim_operation"]["preset_5_min"]), 
                 KeyboardButton(text=i18n["trim_operation"]["preset_10_min"])]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        
        # Ask for end time with localized message
        await message.answer(
            i18n["trim_operation"]["end_time"],
            reply_markup=keyboard
        )
        
        # Update state
        await state.set_state(VideoProcessingStates.waiting_for_trim_end)
        
    except ValueError:
        await message.answer("❌ Please enter a valid time format (seconds, MM:SS or H:MM:SS):")


@router.message(StateFilter(VideoProcessingStates.waiting_for_trim_end))
async def process_trim_end(message: Message, state: FSMContext) -> None:
    """
    Process end time for trimming.
    
    Args:
        message: Message with end time
        state: FSM context for the user
    """
    text = message.text.strip().lower()
    i18n = await get_i18n_for_user(message.from_user.id)
    
    try:
        # Get the state data
        data = await state.get_data()
        start_time = data.get("trim_start", 0)
        
        # Handle preset options first
        if text == i18n["trim_operation"]["end_of_video"].lower():
            # Trim to the end
            await state.update_data(trim_end=None)
        elif text.startswith("+"):
            # Handle relative time presets
            if text == i18n["trim_operation"]["preset_10_sec"].lower():
                end_time = start_time + 10
            elif text == i18n["trim_operation"]["preset_30_sec"].lower():
                end_time = start_time + 30
            elif text == i18n["trim_operation"]["preset_1_min"].lower():
                end_time = start_time + 60
            elif text == i18n["trim_operation"]["preset_2_min"].lower():
                end_time = start_time + 120
            elif text == i18n["trim_operation"]["preset_5_min"].lower():
                end_time = start_time + 300
            elif text == i18n["trim_operation"]["preset_10_min"].lower():
                end_time = start_time + 600
            else:
                # Try to parse the number after +
                try:
                    value = float(text[1:])
                    end_time = start_time + value
                except ValueError:
                    await message.answer(i18n["trim_operation"]["invalid_time_format"])
                    return
                
            # Store end time in state
            await state.update_data(trim_end=end_time)
        else:
            # Try to parse different time formats
            try:
                end_time = parse_time_format(text)
                
                # Check if end time is valid
                if end_time <= start_time:
                    await message.answer(
                        i18n["trim_operation"]["end_greater_than_start"].format(start_time=start_time)
                    )
                    return
                
                # Store end time in state
                await state.update_data(trim_end=end_time)
            except ValueError:
                await message.answer(i18n["trim_operation"]["invalid_time_format"])
                return
        
        # Убираем клавиатуру
        from aiogram.types import ReplyKeyboardRemove
        
        # Process the video
        processing_msg = await message.answer(
            i18n["trim_operation"]["processing"],
            reply_markup=ReplyKeyboardRemove()
        )
        await process_video(message, state, processing_msg.message_id)
        
    except Exception as e:
        logger.error(f"Error processing trim end: {e}")
        await message.answer(f"❌ An error occurred: {str(e)}. Please try again.")


async def process_video(message: Union[Message, CallbackQuery], state: FSMContext, 
                       edit_message_id: Optional[int] = None) -> None:
    """
    Process the video based on selected operation and parameters.
    
    Args:
        message: Message or CallbackQuery object
        state: FSM context for the user
        edit_message_id: Optional message ID to edit instead of sending new message
    """
    # Set processing state
    await state.set_state(VideoProcessingStates.processing)
    
    # Get message object and chat_id
    if isinstance(message, CallbackQuery):
        msg = message.message
        chat_id = message.message.chat.id
    else:
        msg = message
        chat_id = message.chat.id
    
    # Get state data
    data = await state.get_data()
    video_path_str = data.get("video_path")
    operation = data.get("operation")
    
    if not video_path_str or not operation:
        await msg.answer("❌ Insufficient data for video processing.")
        await state.clear()
        return
    
    video_path = Path(video_path_str)
    
    # Show processing message
    processing_text = "⏳ Processing video..."
    if edit_message_id:
        try:
            await msg.bot.edit_message_text(
                chat_id=chat_id,
                message_id=edit_message_id,
                text=processing_text
            )
        except TelegramBadRequest as e:
            # Ignore message not modified errors
            if "message is not modified" in str(e):
                pass
            else:
                # For other errors, log and continue
                logger.error(f"TelegramBadRequest in process_video: {e}")
    else:
        try:
            await msg.edit_text(processing_text)
        except TelegramBadRequest as e:
            if "message is not modified" in str(e):
                pass
            else:
                logger.error(f"TelegramBadRequest in process_video: {e}")
    
    try:
        result_file = None
        
        # Получаем локализацию
        i18n = await get_i18n_for_user(chat_id)

        # Process based on operation
        if operation == "convert":
            target_format = data.get("target_format")
            result_file = video_processor.convert_format(video_path, target_format)
            operation_text = f"{i18n['convert_operation']['result_text']} {target_format.upper()}"
        
        elif operation == "compress":
            quality = data.get("quality", "medium")
            result_file = video_processor.compress_video(video_path, quality)
            quality_text = {
                "high": i18n['compress_operation']['high'],
                "medium": i18n['compress_operation']['medium'],
                "low": i18n['compress_operation']['low']
            }.get(quality, i18n['compress_operation']['medium'])
            operation_text = f"{i18n['compress_operation']['result_text']} {quality_text} {i18n['compress_operation']['quality']}"
        
        elif operation == "extract_audio":
            audio_format = data.get("audio_format", "mp3")
            bitrate = data.get("bitrate", "192k")
            result_file = video_processor.extract_audio(video_path, audio_format, bitrate)
            operation_text = f"{i18n['extract_audio_operation']['result_text']} {audio_format.upper()} {i18n['extract_audio_operation']['with_bitrate']} {bitrate}"
        
        elif operation == "trim":
            trim_start = data.get("trim_start", 0)
            trim_end = data.get("trim_end")
            result_file = video_processor.trim_video(video_path, trim_start, trim_end)
            trim_end_text = f" {i18n['trim_operation']['to']} {trim_end} {i18n['trim_operation']['sec']}" if trim_end else f" {i18n['trim_operation']['to_end']}"
            operation_text = f"{i18n['trim_operation']['result_text']} ({i18n['trim_operation']['from']} {trim_start} {i18n['trim_operation']['sec']}{trim_end_text})"
        
        # Check if processing was successful
        if not result_file:
            raise Exception("Не удалось обработать видео.")
        
        # Получаем локализацию
        i18n = await get_i18n_for_user(chat_id)
        
        # Send the processed file
        success_text = f"{i18n['common']['processing_success']} {operation_text}:"
        if edit_message_id:
            await msg.bot.edit_message_text(
                chat_id=chat_id,
                message_id=edit_message_id,
                text=success_text,
                reply_markup=None  # Убираем клавиатуру
            )
        else:
            await msg.edit_text(
                text=success_text,
                reply_markup=None  # Убираем клавиатуру
            )
        
        # Send file based on type
        if operation == "extract_audio":
            await msg.bot.send_audio(
                chat_id=chat_id,
                audio=FSInputFile(result_file),
                caption=f"{i18n['extract_audio_operation']['caption']} ({data.get('audio_format').upper()}, {data.get('bitrate')})"
            )
        else:
            await msg.bot.send_video(
                chat_id=chat_id,
                video=FSInputFile(result_file),
                caption=f"{i18n['common']['video_result']} {operation_text}"
            )
        
        # Cleanup temporary files
        video_processor.cleanup_temp_file(video_path)
        video_processor.cleanup_temp_file(result_file)
        
    except Exception as e:
        logger.error(f"Error processing video: {str(e)}")
        error_text = f"❌ Произошла ошибка при обработке видео: {str(e)}"
        if edit_message_id:
            await msg.bot.edit_message_text(
                chat_id=chat_id,
                message_id=edit_message_id,
                text=error_text
            )
        else:
            await msg.edit_text(error_text)
    
    # Clear state
    await state.clear()
