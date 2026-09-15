"""
Zieork Mobile Telegram Multi-Channel Dispatcher.
Enables bidirectional communication with your mobile phone via Telegram Bot.
Sends formatted responses, generated files (.xlsx, .docx, .pdf), and voice audio.
"""
import os
import json
import time
import requests
import threading
from typing import Dict, Any, Optional

CONFIG_FILE = os.path.abspath("data/telegram_config.json")
os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)

class TelegramDispatcher:
    def __init__(self):
        self.config_file = CONFIG_FILE
        self.token = self._load_token()
        self.is_polling = False
        self._poll_thread = None

    def _load_token(self) -> str:
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    data = json.load(f)
                    return data.get("bot_token", "").strip()
            except Exception:
                pass
        return os.environ.get("ZIEORK_TELEGRAM_TOKEN", "").strip()

    def set_token(self, token: str) -> Dict[str, Any]:
        """Save Telegram Bot token and verify connectivity with Telegram servers."""
        clean_token = token.strip()
        if not clean_token:
            return {"error": "Token cannot be empty."}

        # Test token with getMe
        try:
            resp = requests.get(f"https://api.telegram.org/bot{clean_token}/getMe", timeout=10)
            data = resp.json()
            if data.get("ok"):
                self.token = clean_token
                with open(self.config_file, "w") as f:
                    json.dump({"bot_token": clean_token, "bot_info": data.get("result", {})}, f, indent=2)
                return {
                    "success": True,
                    "bot_name": data["result"].get("first_name"),
                    "username": data["result"].get("username"),
                    "status": "connected"
                }
            else:
                return {"error": f"Telegram API error: {data.get('description', 'Invalid token')}"}
        except Exception as e:
            return {"error": f"Failed to connect to Telegram: {str(e)}"}

    def get_status(self) -> Dict[str, Any]:
        """Check current Telegram bot connection status."""
        if not self.token:
            return {
                "configured": False,
                "status": "Token not set. You can get a free token from @BotFather on Telegram anytime."
            }

        try:
            resp = requests.get(f"https://api.telegram.org/bot{self.token}/getMe", timeout=8)
            data = resp.json()
            if data.get("ok"):
                return {
                    "configured": True,
                    "status": "online",
                    "bot_name": data["result"].get("first_name"),
                    "username": data["result"].get("username"),
                    "is_polling": self.is_polling
                }
        except Exception:
            pass

        return {"configured": True, "status": "offline_or_unreachable"}

    def send_message(self, chat_id: str, text: str) -> bool:
        """Send a message to a Telegram chat."""
        if not self.token:
            return False
        try:
            url = f"https://api.telegram.org/bot{self.token}/sendMessage"
            resp = requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=10)
            return resp.status_code == 200
        except Exception:
            return False

    def send_document(self, chat_id: str, file_path: str, caption: Optional[str] = None) -> bool:
        """Upload and send a generated file (.xlsx, .docx, .pdf, .mp3, .mp4) to Telegram."""
        if not self.token or not os.path.exists(file_path):
            return False
        try:
            url = f"https://api.telegram.org/bot{self.token}/sendDocument"
            with open(file_path, "rb") as f:
                files = {"document": f}
                data = {"chat_id": chat_id, "caption": caption or os.path.basename(file_path)}
                resp = requests.post(url, data=data, files=files, timeout=20)
                return resp.status_code == 200
        except Exception:
            return False

telegram_dispatcher = TelegramDispatcher()
