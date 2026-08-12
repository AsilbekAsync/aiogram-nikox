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
MYSQL_DB = os.getenv("MYSQL_DB", "nikox")

DATABASE_URL = (
    f"mysql+asyncmy://{MYSQL_USER}:{MYSQL_PASSWORD}@"
    f"{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
)

# Admin
admin_ids_raw = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = [int(x.strip()) for x in admin_ids_raw.split(",")] if admin_ids_raw else []

# App settings
WELCOME_BONUS_UZS = int(os.getenv("WELCOME_BONUS_UZS", "5000"))
REFERRAL_BONUS_UZS = int(os.getenv("REFERRAL_BONUS_UZS", "3000"))
REQUEST_FEE_UZS = int(os.getenv("REQUEST_FEE_UZS", "1000"))
PRIVATE_CONTACT_FEE_UZS = int(os.getenv("PRIVATE_CONTACT_FEE_UZS", "1000"))
SEARCH_ACCESS_FEE_UZS = int(os.getenv("SEARCH_ACCESS_FEE_UZS", "6000"))
HIDDEN_PROFILE_ACCESS_FEE_UZS = int(os.getenv("HIDDEN_PROFILE_ACCESS_FEE_UZS", "6000"))
CHAT_LIFETIME_DAYS = int(os.getenv("CHAT_LIFETIME_DAYS", "7"))

VIP_1_DAY_UZS = int(os.getenv("VIP_1_DAY_UZS", "249000"))
VIP_1_WEEK_UZS = int(os.getenv("VIP_1_WEEK_UZS", "449000"))
VIP_1_MONTH_UZS = int(os.getenv("VIP_1_MONTH_UZS", "990000"))

