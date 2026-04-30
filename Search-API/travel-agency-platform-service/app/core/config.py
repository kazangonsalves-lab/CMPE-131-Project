import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./fallback.db")
    rapidapi_key: str | None = os.getenv("RAPIDAPI_KEY")

def get_settings() -> Settings:
    return Settings()
