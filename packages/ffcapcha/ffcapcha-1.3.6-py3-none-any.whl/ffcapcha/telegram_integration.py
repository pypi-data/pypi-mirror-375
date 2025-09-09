import random
import io
import asyncio
import time
from .captcha import TextCaptcha, MathCaptcha
from .api_client import FFCapchaAPI
from .logger import setup_logger, LOG_MESSAGES

class TelegramCapcha:
    def __init__(self, api_token, API_type="pytelegrambotapi", complexity=3, language="ru", custom_messages=None, period=60, commands="/start", captcha_type="auto", log_level="INFO"):
        self.api = FFCapchaAPI(api_token)
        if not self.api.validate_token():
            raise ValueError("Invalid API token")
        
        self.API_type = API_type.lower()
        self.complexity = max(1, min(complexity, 10))
        self.language = language
        self.custom_messages = custom_messages or {}
        self.period = period
        self.captcha_type = captcha_type.lower()
        self.user_states = {}
        self.user_passed_times = {}
        self.bot = None
        
        if isinstance(commands, str):
            self.commands = [commands]
        else:
            self.commands = commands
        
        self.commands = [cmd if cmd.startswith('/') else f'/{cmd}' for cmd in self.commands]
        
        self.supported_languages = ["en", "ru"]
        if self.language not in self.supported_languages:
            self.language = "en"
        
        self.logger = setup_logger("TelegramCapcha", log_level, language)
        
        self.messages = {
            "ru": {
                "text_captcha_caption": "💻 Введите текст с картинки:",
                "math_captcha_caption": "💻 Решите: {question} = ?",
                "captcha_passed": "✅ Успешно пройдено!",
                "captcha_failed": "❌ Неверно, попробуйте снова",
                "start_captcha": "Напишите /start"
            },
            "en": {
                "text_captcha_caption": "💻 Enter text from image:",
                "math_captcha_caption": "💻 Solve: {question} = ?",
                "captcha_passed": "✅ Successfully completed!",
                "captcha_failed": "❌ Wrong, try again",
                "start_captcha": "Type /start"
            }
        }
        
        if self.custom_messages:
            self._apply_custom_messages()
        
        if self.API_type not in ["aiogram", "pytelegrambotapi", "python-telegram-bot"]:
            raise ValueError("API_type must be 'aiogram', 'pytelegrambotapi', or 'python-telegram-bot'")
        
        bot_info = self.api.get_bot_info()
        bot_name = bot_info.get('name', 'Unknown Bot')
        self.logger.info(LOG_MESSAGES[self.language]["bot_started"].format(bot_name=bot_name))
        self.logger.info(LOG_MESSAGES[self.language]["api_connected"])
    
    def _apply_custom_messages(self):
        current_lang_messages = self.messages.get(self.language, self.messages["en"])
        for key, value in self.custom_messages.items():
            if key in current_lang_messages:
                current_lang_messages[key] = value
    
    def get_message(self, key, **kwargs):
        lang_messages = self.messages.get(self.language, self.messages["en"])
        message = lang_messages.get(key, "")
        
        if key == "start_captcha" and "command" not in kwargs:
            kwargs["command"] = self.commands[0] if self.commands else "/start"
            
        if message and kwargs:
            try:
                return message.format(**kwargs)
            except:
                return message
        return message
    
    def init(self, bot):
        self.bot = bot
        
        if self.API_type == "aiogram":
            self.setup_aiogram_handlers()
        elif self.API_type == "python-telegram-bot":
            self.setup_python_telegram_bot_handlers()
        else:
            self.setup_pytelegrambotapi_handlers()
    
    def setup_pytelegrambotapi_handlers(self):
        try:
            import telebot
            
            @self.bot.message_handler(commands=[cmd.lstrip('/') for cmd in self.commands])
            def command_handler(message):
                self.handle_command_pytelegrambotapi(message)
            
            @self.bot.message_handler(func=lambda message: True, content_types=['text'])
            def text_handler(message):
                self.handle_text_pytelegrambotapi(message)
                
        except ImportError:
            self.logger.error("pyTelegramBotAPI not installed")
    
    def handle_command_pytelegrambotapi(self, message):
        user_id = message.from_user.id
        command = message.text.split()[0] if message.text else ""
        
        if self._needs_captcha(user_id):
            self.send_captcha_pytelegrambotapi(message)
        else:
            self.user_passed_times[user_id] = time.time()
            self.api.log_request(user_id, command, True)
    
    def send_captcha_pytelegrambotapi(self, message):
        user_id = message.from_user.id
        
        if self.captcha_type == "auto":
            captcha_type = "text" if random.random() > 0.5 else "math"
        else:
            captcha_type = self.captcha_type
        
        if captcha_type == "text":
            captcha = TextCaptcha(complexity=self.complexity)
            answer, image = captcha.generate()
            
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            
            self.user_states[user_id] = {
                'type': 'text',
                'answer': answer.lower(),
                'attempts': 0,
                'timestamp': time.time()
            }
            
            self.bot.send_photo(
                chat_id=message.chat.id,
                photo=img_byte_arr,
                caption=self.get_message("text_captcha_caption"),
                parse_mode="HTML"
            )
            
        else:
            captcha = MathCaptcha(complexity=self.complexity)
            answer, question = captcha.generate()
            
            self.user_states[user_id] = {
                'type': 'math',
                'answer': str(answer),
                'attempts': 0,
                'timestamp': time.time()
            }
            
            self.bot.reply_to(
                message,
                self.get_message("math_captcha_caption", question=question),
                parse_mode="HTML"
            )
    
    def handle_text_pytelegrambotapi(self, message):
        user_id = message.from_user.id
        text = message.text.strip()
        
        if user_id in self.user_states:
            captcha_data = self.user_states[user_id]
            
            if captcha_data['type'] == 'text':
                if text.lower() == captcha_data['answer']:
                    self.bot.reply_to(message, self.get_message("captcha_passed"), parse_mode="HTML")
                    self.user_passed_times[user_id] = time.time()
                    self.api.log_captcha_attempt(user_id, True, "text")
                    self.logger.info(f"User {user_id} passed text captcha")
                    del self.user_states[user_id]
                else:
                    captcha_data['attempts'] += 1
                    if captcha_data['attempts'] >= 3:
                        self.bot.reply_to(message, self.get_message("captcha_failed"), parse_mode="HTML")
                        self.api.log_captcha_attempt(user_id, False, "text", {"attempts": captcha_data['attempts']})
                        self.logger.warning(f"User {user_id} failed text captcha")
                        del self.user_states[user_id]
                    else:
                        self.bot.reply_to(message, self.get_message("captcha_failed"), parse_mode="HTML")
            
            elif captcha_data['type'] == 'math':
                if text == captcha_data['answer']:
                    self.bot.reply_to(message, self.get_message("captcha_passed"), parse_mode="HTML")
                    self.user_passed_times[user_id] = time.time()
                    self.api.log_captcha_attempt(user_id, True, "math")
                    self.logger.info(f"User {user_id} passed math captcha")
                    del self.user_states[user_id]
                else:
                    captcha_data['attempts'] += 1
                    if captcha_data['attempts'] >= 3:
                        self.bot.reply_to(message, self.get_message("captcha_failed"), parse_mode="HTML")
                        self.api.log_captcha_attempt(user_id, False, "math", {"attempts": captcha_data['attempts']})
                        self.logger.warning(f"User {user_id} failed math captcha")
                        del self.user_states[user_id]
                    else:
                        self.bot.reply_to(message, self.get_message("captcha_failed"), parse_mode="HTML")
    
    def _needs_captcha(self, user_id):
        current_time = time.time()
        
        if user_id in self.user_passed_times:
            last_passed = self.user_passed_times[user_id]
            period_seconds = self.period * 60
            if current_time - last_passed < period_seconds:
                return False
        
        return True
    
    def set_period(self, period):
        self.period = period
    
    def set_complexity(self, complexity):
        self.complexity = max(1, min(complexity, 10))
    
    def set_captcha_type(self, captcha_type):
        if captcha_type.lower() in ['auto', 'text', 'math']:
            self.captcha_type = captcha_type.lower()
        else:
            raise ValueError("captcha_type must be 'auto', 'text', or 'math'")
    
    def get_user_status(self, user_id):
        needs_captcha = self._needs_captcha(user_id)
        last_passed = self.user_passed_times.get(user_id)
        has_active_captcha = user_id in self.user_states
        
        return {
            'needs_captcha': needs_captcha,
            'last_passed': last_passed,
            'has_active_captcha': has_active_captcha,
            'period_minutes': self.period
        }
    
    def reset_user(self, user_id):
        if user_id in self.user_states:
            del self.user_states[user_id]
        if user_id in self.user_passed_times:
            del self.user_passed_times[user_id]
    
    def get_stats(self):
        return {
            'active_captchas': len(self.user_states),
            'users_passed': len(self.user_passed_times),
            'period_minutes': self.period,
            'complexity': self.complexity,
            'captcha_type': self.captcha_type
        }