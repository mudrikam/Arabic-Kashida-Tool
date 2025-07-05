"""
Settings Manager for Arabic Typing Helper
"""

import os
import json
from constants import DEFAULT_FONTS, UI_SETTINGS

class SettingsManager:
    def __init__(self):
        self.config_path = os.path.join(os.path.dirname(__file__), "config.json")
        self.load_settings()

    def load_settings(self):
        """Load settings from config file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    self.config = json.load(f)
            else:
                self.config = self.get_default_config()
        except:
            self.config = self.get_default_config()

    def get_default_config(self):
        """Get default configuration"""
        return {
            "ui": UI_SETTINGS,
            "fonts": DEFAULT_FONTS,
            "gemini": {
                "api_key": ""
            },
            "appearance": {
                "current_font": "Noto Sans Arabic",
                "current_size": 20,
                "current_mode": "Arab"
            }
        }

    def save_settings(self):
        """Save settings to config file"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except:
            return False

    def get_api_key(self):
        """Get Gemini API key from environment or config"""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            api_key = self.config.get("gemini", {}).get("api_key")
        return api_key

    def save_api_key(self, api_key):
        """Save Gemini API key to config"""
        try:
            if "gemini" not in self.config:
                self.config["gemini"] = {}
            self.config["gemini"]["api_key"] = api_key
            return self.save_settings()
        except:
            return False

    def get_ui_setting(self, key):
        """Get UI setting value"""
        return self.config.get("ui", UI_SETTINGS).get(key, UI_SETTINGS.get(key))

    def save_appearance_settings(self, font_name, font_size, mode):
        """Save appearance settings"""
        try:
            if "appearance" not in self.config:
                self.config["appearance"] = {}
            
            self.config["appearance"]["current_font"] = font_name
            self.config["appearance"]["current_size"] = font_size
            self.config["appearance"]["current_mode"] = mode
            
            return self.save_settings()
        except:
            return False

    def get_appearance_settings(self):
        """Get appearance settings"""
        appearance = self.config.get("appearance", {})
        return {
            "font": appearance.get("current_font", "Noto Sans Arabic"),
            "size": appearance.get("current_size", 20),
            "mode": appearance.get("current_mode", "Arab")
        }
