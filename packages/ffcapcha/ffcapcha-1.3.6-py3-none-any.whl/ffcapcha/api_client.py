# api_client.py
import requests
import json
from datetime import datetime

class FFCapchaAPI:
    def __init__(self, api_token, base_url="https://ffcapcha.pythonanywhere.com"):
        self.api_token = api_token
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        })
    
    def validate_token(self):
        try:
            response = self.session.get(f"{self.base_url}/api/validate", timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def get_bot_info(self):
        try:
            response = self.session.get(f"{self.base_url}/api/bot-info", timeout=10)
            if response.status_code == 200:
                return response.json()
            return {}
        except:
            return {}
    
    def log_captcha_attempt(self, user_id, success, captcha_type, details=None):
        try:
            data = {
                "user_id": user_id,
                "success": success,
                "captcha_type": captcha_type,
                "timestamp": datetime.now().isoformat(),
                "details": details or {}
            }
            response = self.session.post(f"{self.base_url}/api/log/captcha", json=data, timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def log_ban(self, user_id, reason, duration=300):
        try:
            data = {
                "user_id": user_id,
                "reason": reason,
                "duration": duration,
                "timestamp": datetime.now().isoformat()
            }
            response = self.session.post(f"{self.base_url}/api/log/ban", json=data, timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def log_request(self, user_id, command, success=True):
        try:
            data = {
                "user_id": user_id,
                "command": command,
                "success": success,
                "timestamp": datetime.now().isoformat()
            }
            response = self.session.post(f"{self.base_url}/api/log/request", json=data, timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_stats(self, period="day"):
        try:
            params = {"period": period}
            response = self.session.get(f"{self.base_url}/api/stats", params=params, timeout=10)
            if response.status_code == 200:
                return response.json()
            return {}
        except:
            return {}
    
    def get_recent_requests(self, limit=50):
        try:
            params = {"limit": limit}
            response = self.session.get(f"{self.base_url}/api/requests", params=params, timeout=10)
            if response.status_code == 200:
                return response.json().get('requests', [])
            return []
        except:
            return []
    
    def get_banned_users(self):
        try:
            response = self.session.get(f"{self.base_url}/api/bans", timeout=10)
            if response.status_code == 200:
                return response.json().get('bans', [])
            return []
        except:
            return []
    
    def get_captcha_stats(self, captcha_type=None):
        try:
            params = {}
            if captcha_type:
                params["type"] = captcha_type
            response = self.session.get(f"{self.base_url}/api/captcha-stats", params=params, timeout=10)
            if response.status_code == 200:
                return response.json()
            return {}
        except:
            return {}