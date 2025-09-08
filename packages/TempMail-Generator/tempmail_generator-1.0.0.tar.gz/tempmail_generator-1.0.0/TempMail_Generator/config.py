import json
from pathlib import Path

class Config:
    Emails = []
    # to obtain api keys: https://rapidapi.com/calvinloveland335703-0p6BxLYIH8f/api/temp-mail44
    OBTAIN_API_FROM = "https://rapidapi.com/calvinloveland335703-0p6BxLYIH8f/api/temp-mail44"
    CONFIG_PATH = Path("config.json")
    DEFAULT_CONFIG = {
        "rapid_api_keys": [
            "YOUR_API_KEY_1",
            "YOUR_API_KEY_2",
            "YOUR_API_KEY_3"
        ],
        "api_host": "temp-mail44.p.rapidapi.com",
        "api_base_url": "https://temp-mail44.p.rapidapi.com/api/v3"
    }

    CONFIG = DEFAULT_CONFIG
    API_KEYS = None
    KEY_INDEX = 0
    TEMP_MAIL_HEADERS = None
    TEMP_NEW_MAIL_API = None
    TEMP_READ_MAIL_API = None

    @staticmethod
    def load():
        if not Config.CONFIG_PATH.exists():
            Config.CONFIG_PATH.write_text(json.dumps(Config.DEFAULT_CONFIG, indent=4))

        Config.CONFIG = json.loads(Config.CONFIG_PATH.read_text())
        Config.API_KEYS = Config.CONFIG["rapid_api_keys"]
        Config.KEY_INDEX = 0
        Config.TEMP_MAIL_HEADERS = {
            "content-type": "application/json",
            "X-RapidAPI-Key": Config.API_KEYS[Config.KEY_INDEX],
            "X-RapidAPI-Host": Config.CONFIG["api_host"]
        }

        Config.TEMP_NEW_MAIL_API = f"{Config.CONFIG['api_base_url']}/email/new"
        Config.TEMP_READ_MAIL_API = f"{Config.CONFIG['api_base_url']}/email/%s/messages"
    
    @staticmethod
    def save_config():
        return Config.CONFIG_PATH.write_text(json.dumps(Config.CONFIG, indent=4))
