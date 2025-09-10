from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseModel):
    bot_token: str = os.getenv("BOT_TOKEN", "")
    database_url: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./bot.db")
    admin_ids: tuple[int, ...] = tuple(
        int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",")
        if x.strip().lstrip("-").isdigit()
    )
    default_lang: str = os.getenv("DEFAULT_LANG", "uz")

settings = Settings()
