import random
import io
import asyncio
import time
import json
import os
import math
from typing import Dict, Optional, Callable, Any, List, Union
from .captcha import TextCaptcha, MathCaptcha
from .api_client import FFCapchaAPI
from .logger import setup_logger, LOG_MESSAGES

class TelegramCapcha:
    def __init__(self, api_token: str, API_type: str = "pytelegrambotapi", 
                 complexity: int = 3, language: str = "en", 
                 custom_messages: Dict[str, str] = None,
                 period: int = 60,  # Changed from check_periodicity to period
                 commands: Union[str, List[str]] = "/start",
                 captcha_type: str = "auto",  # "auto", "text", or "math"
                 log_level: str = "INFO"):
        
        self.api = FFCapchaAPI(api_token)
        if not self.api.validate_token():
            raise ValueError("Invalid API token. Please get a valid token from FFcapcha dashboard.")
        
        self.API_type = API_type.lower()
        self.complexity = max(1, min(complexity, 10))
        self.language = language
        self.custom_messages = custom_messages or {}
        self.period = period  # Period in minutes for captcha re-check
        self.captcha_type = captcha_type.lower()
        self.user_states: Dict[int, dict] = {}
        self.user_passed_times: Dict[int, float] = {}
        self.bot = None
        
        # Handle commands parameter
        if isinstance(commands, str):
            self.commands = [commands]
        else:
            self.commands = commands
        
        # Ensure commands start with slash
        self.commands = [cmd if cmd.startswith('/') else f'/{cmd}' for cmd in self.commands]
        
        self.supported_languages = ["en", "ru", "es", "de", "fr", "uk"]
        if self.language not in self.supported_languages:
            self.language = "en"
        
        # Setup logger
        self.logger = setup_logger("TelegramCapcha", log_level, language)
        
        self.messages = self._load_default_messages()
        
        if self.custom_messages:
            self._apply_custom_messages()
        
        if self.API_type not in ["aiogram", "pytelegrambotapi", "python-telegram-bot"]:
            raise ValueError("API_type must be 'aiogram', 'pytelegrambotapi', or 'python-telegram-bot'")
        
        # Get bot info for logging
        bot_info = self.api.get_bot_info()
        bot_name = bot_info.get('name', 'Unknown Bot')
        self.logger.info(LOG_MESSAGES[self.language]["bot_started"].format(bot_name=bot_name))
        self.logger.info(LOG_MESSAGES[self.language]["api_connected"])
    
    def _load_default_messages(self) -> Dict[str, Dict[str, str]]:
        return {
            "en": {
                "text_captcha_caption": "💻<b>Request verification</b>\n|-🤝Please, enter text from image:",
                "math_captcha_caption": "💻<b>Request verification</b>\n🤝Please, solve: {question} = ?",
                "captcha_passed": "✅Successfully completed, thank you!\n\n📚Powered on FFcapcha",
                "captcha_failed": "❌Wrong answer//captcha\n|-Try again",
                "start_captcha": "Please complete the captcha first with {command}",
            },
            "ru": {
                "text_captcha_caption": "💻<b>Проверка запроса</b>\n|-🤝Пожалуйста, введите текст с картинки:",
                "math_captcha_caption": "💻<b>Проверка запроса</b>\n🤝Пожалуйса, решите: {question} = ?",
                "captcha_passed": "✅Успешно пройдено, спасибо!\n\n📚Powered on FFcapcha",
                "captcha_failed": "❌Неправильный ответ или капча\n|-попробуйте снова",
                "start_captcha": "🪪<b>Боту необходимо проверить ваш запрос</b>\n|-используйте {command}\n\n📚Powered on FFcapcha",
            }
        }
    
    def _apply_custom_messages(self):
        current_lang_messages = self.messages.get(self.language, self.messages["en"])
        for key, value in self.custom_messages.items():
            if key in current_lang_messages:
                current_lang_messages[key] = value
    
    def get_message(self, key: str, **kwargs) -> str:
        lang_messages = self.messages.get(self.language, self.messages["en"])
        message = lang_messages.get(key, "")
        
        # Add default command if not provided
        if key == "start_captcha" and "command" not in kwargs:
            kwargs["command"] = self.commands[0] if self.commands else "/start"
            
        if message and kwargs:
            try:
                return message.format(**kwargs)
            except:
                return message
        return message
    
    def init(self, bot: Any):
        """Initialize bot framework"""
        self.bot = bot
        
        if self.API_type == "aiogram":
            self.setup_aiogram_handlers()
        elif self.API_type == "python-telegram-bot":
            self.setup_python_telegram_bot_handlers()
        else:
            self.setup_pytelegrambotapi_handlers()
    
    def setup_aiogram_handlers(self):
        try:
            from aiogram import Dispatcher, types
            from aiogram.dispatcher import filters
            
            dp = Dispatcher.get_current()
            
            # Command handlers
            for command in self.commands:
                command_name = command.lstrip('/')
                @dp.message_handler(filters.CommandStart() if command_name == "start" else filters.Command(command_name))
                async def aiogram_command_handler(message: types.Message):
                    await self.handle_command_aiogram(message)
            
            # Text message handler for captcha answers
            @dp.message_handler(content_types=types.ContentType.TEXT)
            async def aiogram_text_handler(message: types.Message):
                await self.handle_text_aiogram(message)
                
        except ImportError:
            self.logger.error("Aiogram not installed. Please install it with: pip install aiogram")
    
    async def handle_command_aiogram(self, message: types.Message):
        from aiogram import types
        
        user_id = message.from_user.id
        command = message.get_command()
        
        # Check if user needs captcha
        if self._needs_captcha(user_id):
            await self.send_captcha_aiogram(message)
        else:
            # User already passed captcha recently
            self.user_passed_times[user_id] = time.time()
            self.api.log_request(user_id, command, True)
    
    async def send_captcha_aiogram(self, message: types.Message):
        from aiogram import types
        
        user_id = message.from_user.id
        
        # Choose captcha type
        if self.captcha_type == "auto":
            captcha_type = "text" if random.random() > 0.5 else "math"
        else:
            captcha_type = self.captcha_type
        
        if captcha_type == "text":
            captcha = TextCaptcha(complexity=self.complexity)
            answer, image = captcha.generate()
            
            # Convert PIL image to bytes
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            
            # Store captcha data
            self.user_states[user_id] = {
                'type': 'text',
                'answer': answer.lower(),
                'attempts': 0,
                'timestamp': time.time()
            }
            
            # Send captcha image
            await self.bot.send_photo(
                chat_id=message.chat.id,
                photo=types.InputFile(img_byte_arr, filename="captcha.png"),
                caption=self.get_message("text_captcha_caption"),
                parse_mode="HTML"
            )
            
        else:  # math
            captcha = MathCaptcha(complexity=self.complexity)
            answer, question = captcha.generate()
            
            self.user_states[user_id] = {
                'type': 'math',
                'answer': str(answer),
                'attempts': 0,
                'timestamp': time.time()
            }
            
            await message.reply(
                self.get_message("math_captcha_caption", question=question),
                parse_mode="HTML"
            )
    
    async def handle_text_aiogram(self, message: types.Message):
        from aiogram import types
        
        user_id = message.from_user.id
        text = message.text.strip()
        
        if user_id in self.user_states:
            captcha_data = self.user_states[user_id]
            
            if captcha_data['type'] == 'text':
                expected = captcha_data['answer']
                if text.lower() == expected:
                    # Captcha passed
                    await message.reply(self.get_message("captcha_passed"), parse_mode="HTML")
                    self.user_passed_times[user_id] = time.time()
                    self.api.log_captcha_attempt(user_id, True, "text")
                    self.logger.info(LOG_MESSAGES[self.language]["captcha_passed"].format(user_id=user_id))
                    del self.user_states[user_id]
                else:
                    # Captcha failed
                    captcha_data['attempts'] += 1
                    if captcha_data['attempts'] >= 3:
                        await message.reply(self.get_message("captcha_failed"), parse_mode="HTML")
                        self.api.log_captcha_attempt(user_id, False, "text", {"attempts": captcha_data['attempts']})
                        self.logger.warning(LOG_MESSAGES[self.language]["captcha_failed"].format(user_id=user_id))
                        del self.user_states[user_id]
                    else:
                        await message.reply(self.get_message("captcha_failed"), parse_mode="HTML")
            
            elif captcha_data['type'] == 'math':
                if text == captcha_data['answer']:
                    await message.reply(self.get_message("captcha_passed"), parse_mode="HTML")
                    self.user_passed_times[user_id] = time.time()
                    self.api.log_captcha_attempt(user_id, True, "math")
                    self.logger.info(LOG_MESSAGES[self.language]["captcha_passed"].format(user_id=user_id))
                    del self.user_states[user_id]
                else:
                    captcha_data['attempts'] += 1
                    if captcha_data['attempts'] >= 3:
                        await message.reply(self.get_message("captcha_failed"), parse_mode="HTML")
                        self.api.log_captcha_attempt(user_id, False, "math", {"attempts": captcha_data['attempts']})
                        self.logger.warning(LOG_MESSAGES[self.language]["captcha_failed"].format(user_id=user_id))
                        del self.user_states[user_id]
                    else:
                        await message.reply(self.get_message("captcha_failed"), parse_mode="HTML")
    
    def setup_pytelegrambotapi_handlers(self):
        try:
            import telebot
            
            @self.bot.message_handler(commands=[cmd.lstrip('/') for cmd in self.commands])
            def pytelegrambotapi_command_handler(message):
                self.handle_command_pytelegrambotapi(message)
            
            @self.bot.message_handler(func=lambda message: True, content_types=['text'])
            def pytelegrambotapi_text_handler(message):
                self.handle_text_pytelegrambotapi(message)
                
        except ImportError:
            self.logger.error("pyTelegramBotAPI not installed. Please install it with: pip install pyTelegramBotAPI")
    
    def handle_command_pytelegrambotapi(self, message):
        import telebot
        
        user_id = message.from_user.id
        command = message.text.split()[0] if message.text else ""
        
        if self._needs_captcha(user_id):
            self.send_captcha_pytelegrambotapi(message)
        else:
            self.user_passed_times[user_id] = time.time()
            self.api.log_request(user_id, command, True)
    
    def send_captcha_pytelegrambotapi(self, message):
        import telebot
        
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
        import telebot
        
        user_id = message.from_user.id
        text = message.text.strip()
        
        if user_id in self.user_states:
            captcha_data = self.user_states[user_id]
            
            if captcha_data['type'] == 'text':
                if text.lower() == captcha_data['answer']:
                    self.bot.reply_to(message, self.get_message("captcha_passed"), parse_mode="HTML")
                    self.user_passed_times[user_id] = time.time()
                    self.api.log_captcha_attempt(user_id, True, "text")
                    self.logger.info(LOG_MESSAGES[self.language]["captcha_passed"].format(user_id=user_id))
                    del self.user_states[user_id]
                else:
                    captcha_data['attempts'] += 1
                    if captcha_data['attempts'] >= 3:
                        self.bot.reply_to(message, self.get_message("captcha_failed"), parse_mode="HTML")
                        self.api.log_captcha_attempt(user_id, False, "text", {"attempts": captcha_data['attempts']})
                        self.logger.warning(LOG_MESSAGES[self.language]["captcha_failed"].format(user_id=user_id))
                        del self.user_states[user_id]
                    else:
                        self.bot.reply_to(message, self.get_message("captcha_failed"), parse_mode="HTML")
            
            elif captcha_data['type'] == 'math':
                if text == captcha_data['answer']:
                    self.bot.reply_to(message, self.get_message("captcha_passed"), parse_mode="HTML")
                    self.user_passed_times[user_id] = time.time()
                    self.api.log_captcha_attempt(user_id, True, "math")
                    self.logger.info(LOG_MESSAGES[self.language]["captcha_passed"].format(user_id=user_id))
                    del self.user_states[user_id]
                else:
                    captcha_data['attempts'] += 1
                    if captcha_data['attempts'] >= 3:
                        self.bot.reply_to(message, self.get_message("captcha_failed"), parse_mode="HTML")
                        self.api.log_captcha_attempt(user_id, False, "math", {"attempts": captcha_data['attempts']})
                        self.logger.warning(LOG_MESSAGES[self.language]["captcha_failed"].format(user_id=user_id))
                        del self.user_states[user_id]
                    else:
                        self.bot.reply_to(message, self.get_message("captcha_failed"), parse_mode="HTML")
    
    def setup_python_telegram_bot_handlers(self):
        try:
            from telegram.ext import CommandHandler, MessageHandler, Filters
            
            application = self.bot
            
            for command in self.commands:
                command_name = command.lstrip('/')
                handler = CommandHandler(command_name, self.handle_command_python_telegram_bot)
                application.add_handler(handler)
            
            text_handler = MessageHandler(Filters.text & ~Filters.command, self.handle_text_python_telegram_bot)
            application.add_handler(text_handler)
            
        except ImportError:
            self.logger.error("python-telegram-bot not installed. Please install it with: pip install python-telegram-bot")
    
    def handle_command_python_telegram_bot(self, update, context):
        user_id = update.effective_user.id
        command = update.message.text.split()[0] if update.message.text else ""
        
        if self._needs_captcha(user_id):
            self.send_captcha_python_telegram_bot(update, context)
        else:
            self.user_passed_times[user_id] = time.time()
            self.api.log_request(user_id, command, True)
    
    def send_captcha_python_telegram_bot(self, update, context):
        from telegram import InputFile
        
        user_id = update.effective_user.id
        
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
            
            context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=InputFile(img_byte_arr, filename="captcha.png"),
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
            
            update.message.reply_text(
                self.get_message("math_captcha_caption", question=question),
                parse_mode="HTML"
            )
    
    def handle_text_python_telegram_bot(self, update, context):
        user_id = update.effective_user.id
        text = update.message.text.strip()
        
        if user_id in self.user_states:
            captcha_data = self.user_states[user_id]
            
            if captcha_data['type'] == 'text':
                if text.lower() == captcha_data['answer']:
                    update.message.reply_text(self.get_message("captcha_passed"), parse_mode="HTML")
                    self.user_passed_times[user_id] = time.time()
                    self.api.log_captcha_attempt(user_id, True, "text")
                    self.logger.info(LOG_MESSAGES[self.language]["captcha_passed"].format(user_id=user_id))
                    del self.user_states[user_id]
                else:
                    captcha_data['attempts'] += 1
                    if captcha_data['attempts'] >= 3:
                        update.message.reply_text(self.get_message("captcha_failed"), parse_mode="HTML")
                        self.api.log_captcha_attempt(user_id, False, "text", {"attempts": captcha_data['attempts']})
                        self.logger.warning(LOG_MESSAGES[self.language]["captcha_failed"].format(user_id=user_id))
                        del self.user_states[user_id]
                    else:
                        update.message.reply_text(self.get_message("captcha_failed"), parse_mode="HTML")
            
            elif captcha_data['type'] == 'math':
                if text == captcha_data['answer']:
                    update.message.reply_text(self.get_message("captcha_passed"), parse_mode="HTML")
                    self.user_passed_times[user_id] = time.time()
                    self.api.log_captcha_attempt(user_id, True, "math")
                    self.logger.info(LOG_MESSAGES[self.language]["captcha_passed"].format(user_id=user_id))
                    del self.user_states[user_id]
                else:
                    captcha_data['attempts'] += 1
                    if captcha_data['attempts'] >= 3:
                        update.message.reply_text(self.get_message("captcha_failed"), parse_mode="HTML")
                        self.api.log_captcha_attempt(user_id, False, "math", {"attempts": captcha_data['attempts']})
                        self.logger.warning(LOG_MESSAGES[self.language]["captcha_failed"].format(user_id=user_id))
                        del self.user_states[user_id]
                    else:
                        update.message.reply_text(self.get_message("captcha_failed"), parse_mode="HTML")
    
    def _needs_captcha(self, user_id: int) -> bool:
        """Check if user needs captcha based on period setting"""
        current_time = time.time()
        
        if user_id in self.user_passed_times:
            last_passed = self.user_passed_times[user_id]
            # Convert period from minutes to seconds
            period_seconds = self.period * 60
            if current_time - last_passed < period_seconds:
                return False
        
        return True
    
    def set_period(self, period: int):
        """Set the period for captcha re-check (in minutes)"""
        self.period = period
    
    def set_complexity(self, complexity: int):
        """Set captcha complexity (1-10)"""
        self.complexity = max(1, min(complexity, 10))
    
    def set_captcha_type(self, captcha_type: str):
        """Set captcha type: 'auto', 'text', or 'math'"""
        if captcha_type.lower() in ['auto', 'text', 'math']:
            self.captcha_type = captcha_type.lower()
        else:
            raise ValueError("captcha_type must be 'auto', 'text', or 'math'")
    
    def get_user_status(self, user_id: int) -> Dict:
        """Get user captcha status"""
        needs_captcha = self._needs_captcha(user_id)
        last_passed = self.user_passed_times.get(user_id)
        has_active_captcha = user_id in self.user_states
        
        return {
            'needs_captcha': needs_captcha,
            'last_passed': last_passed,
            'has_active_captcha': has_active_captcha,
            'period_minutes': self.period
        }
    
    def reset_user(self, user_id: int):
        """Reset user captcha state"""
        if user_id in self.user_states:
            del self.user_states[user_id]
        if user_id in self.user_passed_times:
            del self.user_passed_times[user_id]
    
    def get_stats(self) -> Dict:
        """Get current statistics"""
        return {
            'active_captchas': len(self.user_states),
            'users_passed': len(self.user_passed_times),
            'period_minutes': self.period,
            'complexity': self.complexity,
            'captcha_type': self.captcha_type
        }