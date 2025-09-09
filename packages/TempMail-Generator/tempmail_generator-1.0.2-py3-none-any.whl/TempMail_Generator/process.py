import hashlib
import requests
from .config import Config

class Email:
    def __init__(self, email: str, token: str):
        self.EMAIL = email
        self.TOKEN = token
        self.HASH = hashlib.md5(f"[{self.EMAIL}]:[{self.TOKEN}]".encode()).hexdigest()

    def read_inbox(self):
        response = requests.get(Config.TEMP_READ_MAIL_API % self.EMAIL, headers=Config.TEMP_MAIL_HEADERS)
        try:
            response.raise_for_status()
        except Exception as e:
            raise RuntimeError(f"ReadInboxError: {e}")
        return response.json()

class APIProcess:
    @staticmethod
    def __get_req():
        Config.TEMP_MAIL_HEADERS['X-RapidAPI-Key'] = Config.API_KEYS[Config.KEY_INDEX]
        try:
            response = requests.post(Config.TEMP_NEW_MAIL_API, headers=Config.TEMP_MAIL_HEADERS)
            # response.raise_for_status()
        except requests.RequestException as e:
            raise RuntimeError(f"GenerateEmailError: {e}")
        return response.json()

    @staticmethod
    def generate_email():
        Config.load()
        if not Config.API_KEYS or Config.API_KEYS[0].startswith("YOUR_API_KEY"):
            raise RuntimeError(f"Missing API Key! Obtain from: {Config.OBTAIN_API_FROM}")
        data = APIProcess.__get_req()
        while not data.get("email"):
            Config.KEY_INDEX += 1
            if Config.KEY_INDEX >= len(Config.API_KEYS):
                raise RuntimeError(f"ResponseError: {data}")
            data = APIProcess.__get_req()
        email_obj = Email(data['email'], data['token'])
        Config.Emails.append(email_obj)
        return email_obj
