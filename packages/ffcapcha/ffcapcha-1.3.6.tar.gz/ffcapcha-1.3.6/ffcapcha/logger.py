import logging
import sys

class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[94m',
        'INFO': '\033[92m',
        'WARNING': '\033[93m',
        'ERROR': '\033[91m',
        'CRITICAL': '\033[95m',
        'RESET': '\033[0m'
    }

    def format(self, record):
        level_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        message = super().format(record)
        return f"{level_color}{message}{self.COLORS['RESET']}"

def setup_logger(name="FFcapcha", level="INFO", language="en", log_file=None):
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    logger.handlers.clear()
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_formatter = ColoredFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger

LOG_MESSAGES = {
    "en": {
        "bot_started": "Bot successfully started: {bot_name}",
        "user_banned": "User {user_id} banned for {duration}s: {reason}",
        "captcha_passed": "User {user_id} passed captcha successfully",
        "captcha_failed": "User {user_id} failed captcha",
        "request_blocked": "Request from {user_id} blocked (anti-spam)",
        "api_connected": "Successfully connected to FFcapcha API",
        "api_error": "API connection error: {error}"
    },
    "ru": {
        "bot_started": "Бот успешно запущен: {bot_name}",
        "user_banned": "Пользователь {user_id} забанен на {duration}с: {reason}",
        "captcha_passed": "Пользователь {user_id} успешно прошел капчу",
        "captcha_failed": "Пользователь {user_id} не прошел капчу",
        "request_blocked": "Запрос от {user_id} заблокирован (анти-спам)",
        "api_connected": "Успешное подключение к FFcapcha API",
        "api_error": "Ошибка подключения к API: {error}"
    }
}