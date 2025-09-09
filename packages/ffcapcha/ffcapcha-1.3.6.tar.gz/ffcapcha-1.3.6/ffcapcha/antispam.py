# antispam.py
import time
from collections import defaultdict
from .api_client import FFCapchaAPI
from .logger import setup_logger, LOG_MESSAGES

class AntiSpam:
    def __init__(self, api_token, max_repeats=3, cooldown=10, ban_time=300, max_simultaneous=5, language="en", log_level="INFO", custom_messages=None, enable_auto_ban=True):
        self.api = FFCapchaAPI(api_token)
        if not self.api.validate_token():
            raise ValueError("Invalid API token")
        
        self.max_repeats = max_repeats
        self.cooldown = cooldown
        self.ban_time = ban_time
        self.max_simultaneous = max_simultaneous
        self.language = language
        self.enable_auto_ban = enable_auto_ban
        
        self.logger = setup_logger("AntiSpam", log_level, language)
        self.custom_messages = custom_messages or {}
        
        self.user_requests = defaultdict(list)
        self.user_bans = {}
        self.command_counts = defaultdict(int)
        self.last_reset = time.time()
        
        self.messages = self._load_messages()
        if self.custom_messages:
            self._apply_custom_messages()
        
        self.logger.info(LOG_MESSAGES[self.language]["api_connected"])
    
    def _load_messages(self):
        base_messages = {
            "en": {
                "too_many_requests": "Too many requests. Please wait.",
                "request_too_fast": "Request too fast. Please slow down.",
                "user_banned": "User {user_id} banned for {ban_time} seconds: {reason}",
                "banned_message": "You are temporarily banned due to suspicious activity."
            },
            "ru": {
                "too_many_requests": "Слишком много запросов. Пожалуйста, подождите.",
                "request_too_fast": "Слишком быстрые запросы. Пожалуйста, замедлитесь.",
                "user_banned": "Пользователь {user_id} забанен на {ban_time} секунд: {reason}",
                "banned_message": "Вы временно заблокированы за подозрительную активность."
            }
        }
        return base_messages.get(self.language, base_messages["en"])
    
    def _apply_custom_messages(self):
        for key, value in self.custom_messages.items():
            if key in self.messages:
                self.messages[key] = value
    
    def get_message(self, key, **kwargs):
        message = self.messages.get(key, "")
        if message and kwargs:
            try:
                return message.format(**kwargs)
            except:
                return message
        return message
    
    def add_request(self, user_id, command):
        current_time = time.time()
        reason = ""
        
        if self._is_banned(user_id, current_time):
            self.logger.info(f"Request from {user_id} blocked (banned)")
            return False, "banned"
        
        if current_time - self.last_reset > 60:
            self.command_counts.clear()
            self.last_reset = current_time
        
        self.command_counts[command] += 1
        if self.command_counts[command] > self.max_simultaneous:
            reason = self.get_message("too_many_requests")
            if self.enable_auto_ban:
                self._ban_user(user_id, current_time, reason)
            return False, reason
        
        user_requests = self.user_requests[user_id]
        user_requests.append(current_time)
        user_requests = [t for t in user_requests if current_time - t < 60]
        self.user_requests[user_id] = user_requests
        
        if len(user_requests) > self.max_repeats:
            reason = self.get_message("too_many_requests")
            if self.enable_auto_ban:
                self._ban_user(user_id, current_time, reason)
            return False, reason
        
        if len(user_requests) > 1 and (current_time - user_requests[-2]) < self.cooldown:
            reason = self.get_message("request_too_fast")
            if self.enable_auto_ban:
                self._ban_user(user_id, current_time, reason)
            return False, reason
        
        return True, ""
    
    def _is_banned(self, user_id, current_time):
        if user_id in self.user_bans:
            ban_time, _ = self.user_bans[user_id]
            if current_time - ban_time < self.ban_time:
                return True
            else:
                del self.user_bans[user_id]
        return False
    
    def _ban_user(self, user_id, current_time, reason):
        self.user_bans[user_id] = (current_time, reason)
        self.api.log_ban(user_id, reason, self.ban_time)
        self.logger.info(f"User {user_id} banned for {self.ban_time}s: {reason}")
    
    def manual_ban_user(self, user_id, reason="Manual ban", duration=None):
        ban_duration = duration or self.ban_time
        self.user_bans[user_id] = (time.time(), reason)
        self.api.log_ban(user_id, reason, ban_duration)
        self.logger.info(f"User {user_id} manually banned for {ban_duration}s: {reason}")
    
    def check_ban(self, user_id):
        current_time = time.time()
        if user_id in self.user_bans:
            ban_time, reason = self.user_bans[user_id]
            if current_time - ban_time < self.ban_time:
                return True, reason
            else:
                del self.user_bans[user_id]
        return False, None
    
    def get_ban_message(self):
        return self.get_message("banned_message")
    
    def unban_user(self, user_id):
        if user_id in self.user_bans:
            del self.user_bans[user_id]
            self.logger.info(f"User {user_id} unbanned")
    
    def get_user_stats(self, user_id):
        return {
            "total_requests": len(self.user_requests.get(user_id, [])),
            "is_banned": user_id in self.user_bans,
            "ban_reason": self.user_bans[user_id][1] if user_id in self.user_bans else None
        }
    
    def get_stats(self):
        return {
            "total_bans": len(self.user_bans),
            "active_requests": sum(len(v) for v in self.user_requests.values()),
            "command_stats": dict(self.command_counts),
            "unique_users": len(self.user_requests)
        }
    
    def set_cooldown(self, cooldown):
        self.cooldown = cooldown
    
    def set_ban_time(self, ban_time):
        self.ban_time = ban_time
    
    def set_max_repeats(self, max_repeats):
        self.max_repeats = max_repeats
    
    def enable_auto_banning(self, enable):
        self.enable_auto_ban = enable