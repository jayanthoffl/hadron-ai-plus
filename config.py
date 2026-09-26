import os
from dotenv import load_dotenv

from gemini_pool import gemini_key_pool

load_dotenv()


class Settings:
    @property
    def GEMINI_API_KEY(self):
        return gemini_key_pool.get_current_key()

    @property
    def GEMINI_API_KEYS(self):
        return gemini_key_pool.keys

    ENV = os.getenv("HADRON_ENV", "development")
    PORT = int(os.getenv("HADRON_PORT", "5000"))

    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-flash-lite-latest")
    GEMINI_FALLBACK_MODEL = os.getenv("GEMINI_FALLBACK_MODEL", "gemini-3.1-flash-lite")


settings = Settings()