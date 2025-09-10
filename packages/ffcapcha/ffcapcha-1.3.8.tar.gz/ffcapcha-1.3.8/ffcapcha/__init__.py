from .captcha import TextCaptcha, MathCaptcha
from .antispam import AntiSpam
from .telegram_integration import TelegramCapcha
from .console import ConsoleManager
from .api_client import FFCapchaAPI
from .logger import setup_logger

__version__ = "1.3.8"
__author__ = "VndFF"
__all__ = [
    'TextCaptcha',
    'MathCaptcha', 
    'AntiSpam',
    'TelegramCapcha',
    'ConsoleManager',
    'FFCapchaAPI',
    'setup_logger'
]