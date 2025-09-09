# logger.py
import logging
import sys
from typing import Dict, Optional
from datetime import datetime

class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[94m',    # Blue
        'INFO': '\033[92m',     # Green
        'WARNING': '\033[93m',  # Yellow
        'ERROR': '\033[91m',    # Red
        'CRITICAL': '\033[95m', # Magenta
        'RESET': '\033[0m'      # Reset
    }

    def format(self, record):
        level_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        message = super().format(record)
        return f"{level_color}{message}{self.COLORS['RESET']}"

def setup_logger(name: str = "FFcapcha", level: str = "INFO", 
                language: str = "en", log_file: Optional[str] = None) -> logging.Logger:
    """
    Setup logger with colored output and multilingual support
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_formatter = ColoredFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger

# Multilingual log messages
LOG_MESSAGES = {
    "en": {
        "bot_started": "Bot successfully started: {bot_name}",
        "user_banned": "User {user_id} banned for {duration}s: {reason}",
        "captcha_passed": "User {user_id} passed captcha successfully",
        "captcha_failed": "User {user_id} failed captcha",
        "request_blocked": "Request from {user_id} blocked (anti-spam)",
        "api_connected": "Successfully connected to FFcapcha API",
        "api_error": "API connection error: {error}",
        "console_started": "FFcapcha console manager started",
        "stats_updated": "Statistics updated successfully"
    },
    "ru": {
        "bot_started": "Бот успешно запущен: {bot_name}",
        "user_banned": "Пользователь {user_id} забанен на {duration}с: {reason}",
        "captcha_passed": "Пользователь {user_id} успешно прошел капчу",
        "captcha_failed": "Пользователь {user_id} не прошел капчу",
        "request_blocked": "Запрос от {user_id} заблокирован (анти-спам)",
        "api_connected": "Успешное подключение к FFcapcha API",
        "api_error": "Ошибка подключения к API: {error}",
        "console_started": "Консольный менеджер FFcapcha запущен",
        "stats_updated": "Статистика успешно обновлена"
    }
}