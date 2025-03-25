"""
Localization module for the video converter bot.
Provides translations for bot messages in multiple languages.
"""
from typing import Dict, Any, Optional

# Default language
DEFAULT_LANGUAGE = "ru"

# User language cache
USER_LANGUAGES: Dict[int, str] = {}

# Available languages
LANGUAGES = {
    "ru": "Русский",
    "en": "English",
    "uz": "O'zbek"
}

# Translations dictionary
TRANSLATIONS: Dict[str, Dict[str, Dict[str, str]]] = {
    # Общие фразы и кнопки
    "common": {
        "ru": {
            "back": "Назад",
            "cancel": "Отмена",
            "operation_canceled": "❌ Операция отменена.",
            "processing_success": "✅ Видео успешно обработано! Результат",
            "video_result": "Видео после"
        },
        "en": {
            "back": "Back",
            "cancel": "Cancel",
            "operation_canceled": "❌ Operation canceled.",
            "processing_success": "✅ Video successfully processed! Result of",
            "video_result": "Video after"
        },
        "uz": {
            "back": "Orqaga",
            "cancel": "Bekor qilish",
            "operation_canceled": "❌ Operatsiya bekor qilindi.",
            "processing_success": "✅ Video muvaffaqiyatli qayta ishlandi! Natija",
            "video_result": "Video keyin"         
        }
    },
    
    # Конвертация
    "convert_operation": {
        "ru": {
            "result_text": "конвертации в"
        },
        "en": {
            "result_text": "conversion to"
        },
        "uz": {
            "result_text": "konvertatsiya"
        }
    },
    
    # Сжатие
    "compress_operation": {
        "ru": {
            "high_quality": "Высокое качество",
            "medium_quality": "Среднее качество",
            "low_quality": "Низкое качество", 
            "high": "высоким",
            "medium": "средним",
            "low": "низким",
            "quality": "качеством",
            "result_text": "сжатия с"
        },
        "en": {
            "high_quality": "High quality",
            "medium_quality": "Medium quality",
            "low_quality": "Low quality",
            "high": "high",
            "medium": "medium",
            "low": "low",
            "quality": "quality",
            "result_text": "compression with"
        },
        "uz": {
            "high_quality": "Yuqori sifat",
            "medium_quality": "O'rta sifat",
            "low_quality": "Past sifat",
            "high": "yuqori",
            "medium": "o'rta",
            "low": "past",
            "quality": "sifat",
            "result_text": "siqish"
        }
    },
    
    # Извлечение аудио
    "extract_audio_operation": {
        "ru": {
            "result_text": "извлечения аудио в формате",
            "with_bitrate": "с битрейтом",
            "caption": "Аудио извлечено из видео"
        },
        "en": {
            "result_text": "audio extraction in format",
            "with_bitrate": "with bitrate",
            "caption": "Audio extracted from video"
        },
        "uz": {
            "result_text": "audio chiqarish formatida",
            "with_bitrate": "bitreyt bilan",
            "caption": "Videodan audio chiqarildi"
        }
    },
    
    # Обрезка видео
    "trim_operation": {
        "ru": {
            "to": "до",
            "sec": "сек",
            "to_end": "до конца",
            "result_text": "обрезки",
            "from": "с",
            "start_time": "✂️ Введите время начала отрезка (в секундах или в формате MM:SS):",
            "end_time": "✂️ Введите время конца отрезка (в секундах, формате MM:SS или выберите из вариантов):",
            "invalid_time_format": "❌ Неверный формат времени. Пожалуйста, укажите время в секундах или в формате MM:SS:",
            "positive_time": "❌ Время начала должно быть положительным числом. Попробуйте снова:",
            "end_greater_than_start": "❌ Время конца должно быть больше времени начала ({start_time}). Попробуйте снова:",
            "end_of_video": "Конец видео",
            "preset_10_sec": "+10 сек",
            "preset_30_sec": "+30 сек",
            "preset_1_min": "+1 мин",
            "preset_2_min": "+2 мин",
            "preset_5_min": "+5 мин",
            "preset_10_min": "+10 мин",
            "processing": "⏳ Обрабатываю видео...",
            "error_occurred": "❌ Произошла ошибка: {error}. Пожалуйста, попробуйте снова.",
            "insufficient_data": "❌ Недостаточно данных для обработки видео."
        },
        "en": {
            "to": "to",
            "sec": "sec",
            "to_end": "to the end",
            "result_text": "trimming",
            "from": "from",
            "start_time": "✂️ Enter the start time of the segment (in seconds or MM:SS format):",
            "end_time": "✂️ Enter end time (seconds, MM:SS format, or select from options):",
            "invalid_time_format": "❌ Invalid time format. Please enter time in seconds or MM:SS format:",
            "positive_time": "❌ Start time should be a positive number. Please try again:",
            "end_greater_than_start": "❌ End time must be greater than start time ({start_time}). Please try again:",
            "end_of_video": "End of video",
            "preset_10_sec": "+10 sec",
            "preset_30_sec": "+30 sec",
            "preset_1_min": "+1 min",
            "preset_2_min": "+2 min",
            "preset_5_min": "+5 min",
            "preset_10_min": "+10 min",
            "processing": "⏳ Processing video...",
            "error_occurred": "❌ An error occurred: {error}. Please try again.",
            "insufficient_data": "❌ Insufficient data for video processing."
        },
        "uz": {
            "to": "gacha",
            "sec": "soniya",
            "to_end": "oxirigacha",
            "result_text": "qirqish",
            "from": "dan",
            "start_time": "✂️ Segment boshlanish vaqtini kiriting (soniyalarda yoki MM:SS formatida):",
            "end_time": "✂️ Tugash vaqtini kiriting (soniyalar, MM:SS formatida yoki variantlardan tanlang):",
            "invalid_time_format": "❌ Noto'g'ri vaqt formati. Iltimos, vaqtni soniyalarda yoki MM:SS formatida kiriting:",
            "positive_time": "❌ Boshlanish vaqti musbat son bo'lishi kerak. Iltimos, qayta urinib ko'ring:",
            "end_greater_than_start": "❌ Tugash vaqti boshlanish vaqtidan katta bo'lishi kerak ({start_time}). Iltimos, qayta urinib ko'ring:",
            "end_of_video": "Video oxiri",
            "preset_10_sec": "+10 soniya",
            "preset_30_sec": "+30 soniya",
            "preset_1_min": "+1 daqiqa",
            "preset_2_min": "+2 daqiqa",
            "preset_5_min": "+5 daqiqa",
            "preset_10_min": "+10 daqiqa",
            "processing": "⏳ Video qayta ishlanmoqda...",
            "error_occurred": "❌ Xatolik yuz berdi: {error}. Iltimos, qayta urinib ko'ring.",
            "insufficient_data": "❌ Video qayta ishlash uchun ma'lumotlar yetarli emas."
        }
    },
    
    # Command descriptions
    "command_descriptions": {
        "ru": {
            "start": "Начать работу с ботом",
            "help": "Показать справку",
            "convert": "Конвертировать видео",
            "compress": "Сжать видео",
            "extract_audio": "Извлечь аудио из видео",
            "trim": "Обрезать видео",
            "cancel": "Отменить текущую операцию",
            "settings": "Настройки бота",
        },
        "en": {
            "start": "Start working with the bot",
            "help": "Show help",
            "convert": "Convert video",
            "compress": "Compress video",
            "extract_audio": "Extract audio from video",
            "trim": "Trim video",
            "cancel": "Cancel current operation",
            "settings": "Bot settings",
        },
        "uz": {
            "start": "Bot bilan ishlashni boshlash",
            "help": "Yordam ko'rsatish",
            "convert": "Videoni konvertatsiya qilish",
            "compress": "Videoni siqish",
            "extract_audio": "Videodan audio ajratib olish",
            "trim": "Videoni qirqish",
            "cancel": "Joriy operatsiyani bekor qilish",
            "settings": "Bot sozlamalari",
        }
    },
    
    # Start command
    "start": {
        "ru": {
            "greeting": "👋 Привет, {username}!\n\nЯ бот для обработки видео. Я могу:\n• Конвертировать видео в разные форматы\n• Сжимать видео с сохранением качества\n• Извлекать аудио из видео\n• Обрезать видео и аудио\n\nОтправьте мне видео или ссылку на видео, чтобы начать.\nДля просмотра доступных команд введите /help.",
        },
        "en": {
            "greeting": "👋 Hello, {username}!\n\nI'm a video processing bot. I can:\n• Convert videos to different formats\n• Compress videos while maintaining quality\n• Extract audio from videos\n• Trim videos and audio\n\nSend me a video or a link to a video to get started.\nTo view available commands, type /help.",
        },
        "uz": {
            "greeting": "👋 Salom, {username}!\n\nMen video qayta ishlash botiman. Men quyidagilarni qila olaman:\n• Videolarni turli formatlarga o'zgartirish\n• Videolarni sifatini saqlagan holda siqish\n• Videodan audio ajratib olish\n• Video va audiolarni qirqish\n\nBoshlash uchun menga video yoki videoga havola yuboring.\nMavjud buyruqlarni ko'rish uchun /help deb yozing.",
        }
    },
    
    # Help command
    "help": {
        "ru": {
            "title": "📋 Список команд",
            "how_to_use": "📝 Как пользоваться",
            "how_to_use_steps": "1. Отправьте видео или ссылку на видео\n2. Выберите действие, которое хотите выполнить\n3. Следуйте инструкциям бота",
            "limitations": "⚠️ Ограничения",
            "max_file_size": "• Максимальный размер файла: {max_file_size} МБ",
            "max_requests": "• Максимальное количество запросов в минуту: {max_requests}",
        },
        "en": {
            "title": "📋 Command List",
            "how_to_use": "📝 How to Use",
            "how_to_use_steps": "1. Send a video or a link to a video\n2. Choose the action you want to perform\n3. Follow the bot's instructions",
            "limitations": "⚠️ Limitations",
            "max_file_size": "• Maximum file size: {max_file_size} MB",
            "max_requests": "• Maximum number of requests per minute: {max_requests}",
        },
        "uz": {
            "title": "📋 Buyruqlar ro'yxati",
            "how_to_use": "📝 Qanday foydalanish",
            "how_to_use_steps": "1. Video yoki videoga havola yuboring\n2. Bajarmoqchi bo'lgan harakatni tanlang\n3. Botning ko'rsatmalariga amal qiling",
            "limitations": "⚠️ Cheklovlar",
            "max_file_size": "• Maksimal fayl hajmi: {max_file_size} MB",
            "max_requests": "• Bir daqiqada maksimal so'rovlar soni: {max_requests}",
        }
    },
    
    # Operation selection
    "operation_selection": {
        "ru": {
            "title": "🎬 Выберите операцию, которую нужно выполнить с видео:",
            "convert": "🔄 Конвертировать",
            "compress": "🗜️ Сжать",
            "extract_audio": "🔊 Извлечь аудио",
            "trim": "✂️ Обрезать",
        },
        "en": {
            "title": "🎬 Select the operation to perform on the video:",
            "convert": "🔄 Convert",
            "compress": "🗜️ Compress",
            "extract_audio": "🔊 Extract audio",
            "trim": "✂️ Trim",
        },
        "uz": {
            "title": "🎬 Video bilan bajarish kerak bo'lgan operatsiyani tanlang:",
            "convert": "🔄 Konvertatsiya",
            "compress": "🗜️ Siqish",
            "extract_audio": "🔊 Audio ajratish",
            "trim": "✂️ Qirqish",
        }
    },
    
    # Format selection
    "format_selection": {
        "ru": {
            "title": "🔄 Выберите формат для конвертации:",
            "cancel": "Отмена",
        },
        "en": {
            "title": "🔄 Select the format for conversion:",
            "cancel": "Cancel",
        },
        "uz": {
            "title": "🔄 Konvertatsiya uchun formatni tanlang:",
            "cancel": "Bekor qilish",
        }
    },
    
    # Quality selection
    "quality_selection": {
        "ru": {
            "title": "🗜️ Выберите качество сжатия:",
            "high": "Высокое качество",
            "medium": "Среднее качество",
            "low": "Низкое качество",
            "cancel": "Отмена",
        },
        "en": {
            "title": "🗜️ Select compression quality:",
            "high": "High quality",
            "medium": "Medium quality",
            "low": "Low quality",
            "cancel": "Cancel",
        },
        "uz": {
            "title": "🗜️ Siqish sifatini tanlang:",
            "high": "Yuqori sifat",
            "medium": "O'rta sifat",
            "low": "Past sifat",
            "cancel": "Bekor qilish",
        }
    },
    
    # Audio format selection
    "audio_format_selection": {
        "ru": {
            "title": "🔊 Выберите формат аудио:",
            "cancel": "Отмена",
        },
        "en": {
            "title": "🔊 Select audio format:",
            "cancel": "Cancel",
        },
        "uz": {
            "title": "🔊 Audio formatini tanlang:",
            "cancel": "Bekor qilish",
        }
    },
    
    # Bitrate selection
    "bitrate_selection": {
        "ru": {
            "title": "🔊 Выберите битрейт аудио:",
            "high": "Высокое (320k)",
            "medium": "Среднее (192k)",
            "low": "Низкое (128k)",
            "cancel": "Отмена",
        },
        "en": {
            "title": "🔊 Select audio bitrate:",
            "high": "High (320k)",
            "medium": "Medium (192k)",
            "low": "Low (128k)",
            "cancel": "Cancel",
        },
        "uz": {
            "title": "🔊 Audio bitreytini tanlang:",
            "high": "Yuqori (320k)",
            "medium": "O'rta (192k)",
            "low": "Past (128k)",
            "cancel": "Bekor qilish",
        }
    },
    
    # Processing status
    "processing_status": {
        "ru": {
            "receiving_video": "⏳ Получаю видео...",
            "downloading_video": "⏳ Загружаю видео по ссылке...",
            "processing_video": "⏳ Обрабатываю видео...",
            "success": "✅ Видео успешно обработано! Результат {operation_text}:",
            "audio_extraction_caption": "Аудио извлечено из видео ({format}, {bitrate})",
            "video_processing_caption": "Видео после {operation_text}",
        },
        "en": {
            "receiving_video": "⏳ Receiving video...",
            "downloading_video": "⏳ Downloading video from link...",
            "processing_video": "⏳ Processing video...",
            "success": "✅ Video successfully processed! Result of {operation_text}:",
            "audio_extraction_caption": "Audio extracted from video ({format}, {bitrate})",
            "video_processing_caption": "Video after {operation_text}",
        },
        "uz": {
            "receiving_video": "⏳ Video qabul qilinmoqda...",
            "downloading_video": "⏳ Havoladan video yuklab olinmoqda...",
            "processing_video": "⏳ Video qayta ishlanmoqda...",
            "success": "✅ Video muvaffaqiyatli qayta ishlandi! {operation_text} natijasi:",
            "audio_extraction_caption": "Videodan ajratilgan audio ({format}, {bitrate})",
            "video_processing_caption": "Video {operation_text} dan keyin",
        }
    },
    
    # Operation descriptions
    "operation_descriptions": {
        "ru": {
            "convert": "конвертации в {format}",
            "compress": "сжатия с {quality} качеством",
            "extract_audio": "извлечения аудио в формате {format} с битрейтом {bitrate}",
            "trim": "обрезки (с {start_time} сек{end_time_text})",
        },
        "en": {
            "convert": "conversion to {format}",
            "compress": "compression with {quality} quality",
            "extract_audio": "audio extraction in {format} format with {bitrate} bitrate",
            "trim": "trimming (from {start_time} sec{end_time_text})",
        },
        "uz": {
            "convert": "{format}ga konvertatsiya",
            "compress": "{quality} sifat bilan siqish",
            "extract_audio": "{format} formatida {bitrate} bitreyt bilan audio ajratish",
            "trim": "qirqish ({start_time} soniyadan{end_time_text})",
        }
    },
    
    # Quality descriptions
    "quality_descriptions": {
        "ru": {
            "high": "высоким",
            "medium": "средним",
            "low": "низким",
        },
        "en": {
            "high": "high",
            "medium": "medium",
            "low": "low",
        },
        "uz": {
            "high": "yuqori",
            "medium": "o'rta",
            "low": "past",
        }
    },
    
    # Error messages
    "errors": {
        "ru": {
            "rate_limit_exceeded": "⚠️ Превышен лимит запросов. Пожалуйста, попробуйте позже.",
            "download_failed": "❌ Не удалось загрузить видео. Убедитесь, что размер файла не превышает {max_file_size} МБ.",
            "url_download_failed": "❌ Не удалось загрузить видео по ссылке. Проверьте ссылку или попробуйте другое видео.",
            "invalid_url": "❌ Неверный формат URL. Пожалуйста, отправьте корректную ссылку на видео.",
            "processing_error": "❌ Произошла ошибка при обработке видео: {error}",
            "no_active_operation": "❌ Нет активной операции для отмены.",
            "operation_canceled": "✅ Текущая операция отменена. Вы можете начать заново.",
            "unauthorized": "❌ У вас нет доступа к этой команде.",
        },
        "en": {
            "rate_limit_exceeded": "⚠️ Rate limit exceeded. Please try again later.",
            "download_failed": "❌ Failed to download the video. Make sure the file size does not exceed {max_file_size} MB.",
            "url_download_failed": "❌ Failed to download the video from the link. Check the link or try another video.",
            "invalid_url": "❌ Invalid URL format. Please send a valid video link.",
            "processing_error": "❌ An error occurred while processing the video: {error}",
            "no_active_operation": "❌ No active operation to cancel.",
            "operation_canceled": "✅ Current operation canceled. You can start again.",
            "unauthorized": "❌ You do not have access to this command.",
        },
        "uz": {
            "rate_limit_exceeded": "⚠️ So'rovlar soni cheklangan. Iltimos, keyinroq qayta urinib ko'ring.",
            "download_failed": "❌ Videoni yuklab olish muvaffaqiyatsiz tugadi. Fayl hajmi {max_file_size} MB dan oshmasligiga ishonch hosil qiling.",
            "url_download_failed": "❌ Havoladan videoni yuklab olish muvaffaqiyatsiz tugadi. Havolani tekshiring yoki boshqa videoni sinab ko'ring.",
            "invalid_url": "❌ Noto'g'ri URL formati. Iltimos, to'g'ri video havolasini yuboring.",
            "processing_error": "❌ Videoni qayta ishlashda xatolik yuz berdi: {error}",
            "no_active_operation": "❌ Bekor qilish uchun faol operatsiya yo'q.",
            "operation_canceled": "✅ Joriy operatsiya bekor qilindi. Siz qaytadan boshlashingiz mumkin.",
            "unauthorized": "❌ Sizda ushbu buyruqqa kirish huquqi yo'q.",
        }
    },
    
    # Settings
    "settings": {
        "ru": {
            "title": "⚙️ Настройки",
            "language": "🌐 Язык: {current_language}",
            "change_language": "Изменить язык",
        },
        "en": {
            "title": "⚙️ Settings",
            "language": "🌐 Language: {current_language}",
            "change_language": "Change language",
        },
        "uz": {
            "title": "⚙️ Sozlamalar",
            "language": "🌐 Til: {current_language}",
            "change_language": "Tilni o'zgartirish",
        }
    },
    
    # Language selection
    "language_selection": {
        "ru": {
            "title": "🌐 Выберите язык:",
            "russian": "Русский",
            "english": "English",
            "uzbek": "O'zbek",
            "language_changed": "✅ Язык изменен на русский.",
        },
        "en": {
            "title": "🌐 Select language:",
            "russian": "Русский",
            "english": "English",
            "uzbek": "O'zbek",
            "language_changed": "✅ Language changed to English.",
        },
        "uz": {
            "title": "🌐 Tilni tanlang:",
            "russian": "Русский",
            "english": "English",
            "uzbek": "O'zbek",
            "language_changed": "✅ Til o'zbek tiliga o'zgartirildi.",
        }
    }
}

async def get_i18n_for_user(user_id: int) -> Dict[str, Dict[str, str]]:
    """
    Get localization dictionary for the user.
    
    Args:
        user_id: Telegram user ID
        
    Returns:
        Dictionary with translations for the user's language
    """
    # Get user language (default to Russian if not set)
    user_lang = USER_LANGUAGES.get(user_id, DEFAULT_LANGUAGE)
    
    # Create a dictionary with all translation sections for the user's language
    i18n = {}
    for section, translations in TRANSLATIONS.items():
        i18n[section] = translations.get(user_lang, translations[DEFAULT_LANGUAGE])
    
    return i18n


def get_text(category: str, key: str, language: str = "ru", **kwargs: Any) -> str:
    """
    Get localized text for the specified category, key, and language.
    
    Args:
        category: Category of the text (e.g., "start", "help", "errors")
        key: Key of the text within the category
        language: Language code (default: "ru")
        **kwargs: Format parameters for the text
        
    Returns:
        Localized text
    """
    # Fallback to Russian if the language is not supported
    if language not in LANGUAGES:
        language = "ru"
    
    # Get the text from the translations dictionary
    try:
        text = TRANSLATIONS[category][language][key]
        # Format the text with the provided parameters
        if kwargs:
            text = text.format(**kwargs)
        return text
    except KeyError:
        # Fallback to Russian if the translation is not available
        try:
            text = TRANSLATIONS[category]["ru"][key]
            if kwargs:
                text = text.format(**kwargs)
            return text
        except KeyError:
            # Return a placeholder if the translation is not found
            return f"[{category}.{key}]"


class UserLanguage:
    """
    Class for managing user language preferences.
    """
    
    def __init__(self):
        self._user_languages: Dict[int, str] = {}
    
    def get_user_language(self, user_id: int) -> str:
        """
        Get the language for a specific user.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Language code (default: "ru")
        """
        return self._user_languages.get(user_id, "ru")
    
    def set_user_language(self, user_id: int, language: str) -> None:
        """
        Set the language for a specific user.
        
        Args:
            user_id: Telegram user ID
            language: Language code
        """
        if language in LANGUAGES:
            self._user_languages[user_id] = language


# Create a global instance
user_language = UserLanguage()
