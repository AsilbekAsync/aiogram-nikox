import os
from typing import cast

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = cast(str, os.getenv("BOT_TOKEN"))
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN .env faylida o'rnatilmagan")

MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DB = os.getenv("MYSQL_DB", "aiogram_start")

DATABASE_URL = (
    f"mysql+asyncmy://{MYSQL_USER}:{MYSQL_PASSWORD}@"
    f"{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
)
