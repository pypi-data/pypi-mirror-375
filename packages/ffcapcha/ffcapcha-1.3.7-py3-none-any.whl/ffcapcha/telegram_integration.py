import random
import io
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
        
        self.msgs = {
            "ru": {
                "text_captcha_caption": "💻<b>Проверка запроса</b>\n|-🤝Пожалуйста, введите текст с картинки:",
                "math_captcha_caption": "💻<b>Проверка запроса</b>\n🤝Пожалуйса, решите: {question} = ?",
                "captcha_passed": "✅Успешно пройдено, спасибо!\n\n📚Powered on FFcapcha",
                "captcha_failed": "❌Неправильный ответ или капча\n|-попробуйте снова",
                "start_captcha": "🪪<b>Боту необходимо проверить ваш запрос</b>\n|-используйте {command}\n\n📚Powered on FFcapcha"
            },
            "en": {
                "text_captcha_caption": "💻<b>Request verification</b>\n|-🤝Please, enter text from image:",
                "math_captcha_caption": "💻<b>Request verification</b>\n🤝Please, solve: {question} = ?",
                "captcha_passed": "✅Successfully completed, thank you!\n\n📚Powered on FFcapcha",
                "captcha_failed": "❌Wrong answer//captcha\n|-Try again",
                "start_captcha": "Please complete the captcha first with {command}"
            }
        }
        
        if self.custom_messages:
            self._apply_custom_msgs()
        
        self.logger.info(LOG_MESSAGES[self.language]["api_connected"])
    
    def _apply_custom_msgs(self):
        for lang in self.supported_languages:
            if lang in self.custom_messages:
                for key, value in self.custom_messages[lang].items():
                    if key in self.msgs[lang]:
                        self.msgs[lang][key] = value
    
    def get_msg(self, key, **kwargs):
        message = self.msgs[self.language].get(key, "")
        if message and kwargs:
            try:
                return message.format(**kwargs)
            except:
                return message
        return message
    
    def init_bot(self, bot):
        self.bot = bot
        bot_info = self.api.get_bot_info()
        bot_name = bot_info.get('name', 'Unknown Bot')
        self.logger.info(LOG_MESSAGES[self.language]["bot_started"].format(bot_name=bot_name))
    
    def _get_captcha_type(self):
        if self.captcha_type == "auto":
            return random.choice(["text", "math"])
        return self.captcha_type
    
    def _generate_captcha(self, user_id):
        captcha_type = self._get_captcha_type()
        
        if captcha_type == "text":
            text_captcha = TextCaptcha(complexity=self.complexity)
            answer, image = text_captcha.generate()
            caption = self.get_msg("text_captcha_caption")
            return answer, image, caption, "text"
        else:
            math_captcha = MathCaptcha(complexity=self.complexity)
            answer, question = math_captcha.generate()
            caption = self.get_msg("math_captcha_caption", question=question)
            return answer, None, caption, "math"
    
    def _send_captcha(self, chat_id, user_id):
        answer, image, caption, captcha_type = self._generate_captcha(user_id)
        
        self.user_states[user_id] = {
            "answer": str(answer),
            "chat_id": chat_id,
            "attempts": 0,
            "captcha_type": captcha_type,
            "timestamp": time.time()
        }
        
        if image:
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            
            if self.API_type == "pytelegrambotapi":
                self.bot.send_photo(chat_id, img_byte_arr, caption=caption, parse_mode="HTML")
            elif self.API_type == "aiogram":
                from aiogram.types import InputFile
                self.bot.send_photo(chat_id, InputFile(img_byte_arr), caption=caption, parse_mode="HTML")
        else:
            if self.API_type == "pytelegrambotapi":
                self.bot.send_message(chat_id, caption, parse_mode="HTML")
            elif self.API_type == "aiogram":
                self.bot.send_message(chat_id, caption, parse_mode="HTML")
        
        return answer
    
    def send_captcha(self, chat_id, user_id):
        return self._send_captcha(chat_id, user_id)
    
    def handle_text(self, message):
        user_id = message.from_user.id
        text = message.text.strip()
        
        if user_id not in self.user_states:
            return False
        
        user_data = self.user_states[user_id]
        
        if text == user_data["answer"]:
            self._captcha_passed(user_id)
            return True
        else:
            user_data["attempts"] += 1
            if user_data["attempts"] >= 3:
                del self.user_states[user_id]
                self._send_captcha(user_data["chat_id"], user_id)
                return False
            
            if self.API_type == "pytelegrambotapi":
                self.bot.send_message(user_data["chat_id"], self.get_msg("captcha_failed"), parse_mode="HTML")
            elif self.API_type == "aiogram":
                self.bot.send_message(user_data["chat_id"], self.get_msg("captcha_failed"), parse_mode="HTML")
            
            return False
    
    def _captcha_passed(self, user_id):
        user_data = self.user_states[user_id]
        chat_id = user_data["chat_id"]
        
        if self.API_type == "pytelegrambotapi":
            self.bot.send_message(chat_id, self.get_msg("captcha_passed"), parse_mode="HTML")
        elif self.API_type == "aiogram":
            self.bot.send_message(chat_id, self.get_msg("captcha_passed"), parse_mode="HTML")
        
        self.user_passed_times[user_id] = time.time()
        del self.user_states[user_id]
        
        self.api.log_captcha(user_id, True, user_data["captcha_type"], {
            "attempts": user_data["attempts"],
            "time_taken": time.time() - user_data["timestamp"]
        })
        
        self.logger.info(LOG_MESSAGES[self.language]["captcha_passed"].format(user_id=user_id))
    
    def check_user(self, user_id):
        current_time = time.time()
        
        if user_id in self.user_passed_times:
            if current_time - self.user_passed_times[user_id] < self.period:
                return True
            else:
                del self.user_passed_times[user_id]
        
        return False
    
    def require_captcha(self, func):
        def wrapper(message):
            user_id = message.from_user.id
            
            if self.check_user(user_id):
                return func(message)
            else:
                if message.text in self.commands:
                    chat_id = message.chat.id
                    self._send_captcha(chat_id, user_id)
                    return
                
                if self.API_type == "pytelegrambotapi":
                    self.bot.send_message(message.chat.id, self.get_msg("start_captcha", command=self.commands[0]), parse_mode="HTML")
                elif self.API_type == "aiogram":
                    self.bot.send_message(message.chat.id, self.get_msg("start_captcha", command=self.commands[0]), parse_mode="HTML")
        
        return wrapper
    
    def set_complexity(self, complexity):
        self.complexity = max(1, min(complexity, 10))
    
    def set_period(self, period):
        self.period = max(10, period)
    
    def set_captcha_type(self, captcha_type):
        allowed_types = ["auto", "text", "math"]
        if captcha_type.lower() in allowed_types:
            self.captcha_type = captcha_type.lower()
    
    def get_user_stats(self, user_id):
        if user_id in self.user_states:
            return {
                "attempts": self.user_states[user_id]["attempts"],
                "captcha_type": self.user_states[user_id]["captcha_type"],
                "time_elapsed": time.time() - self.user_states[user_id]["timestamp"]
            }
        return None
    
    def get_stats(self):
        return {
            "active_captchas": len(self.user_states),
            "passed_users": len(self.user_passed_times),
            "total_attempts": sum(data["attempts"] for data in self.user_states.values())
        }