from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from texts.loader import load

def get_main_menu_kb(lang: str = "uz") -> ReplyKeyboardMarkup:
    t = load(lang, "menu")
    kb = [
        [KeyboardButton(text=t["btn_profile"]), KeyboardButton(text=t["btn_wallet"])],
        [KeyboardButton(text=t["btn_deposit"]), KeyboardButton(text=t["btn_history"])],
        [KeyboardButton(text=t["btn_vip"]), KeyboardButton(text=t["btn_request"])],
        [KeyboardButton(text=t["btn_search"]), KeyboardButton(text=t["btn_hidden"])],
        [KeyboardButton(text=t["btn_chats"]), KeyboardButton(text=t["btn_new_requests"])],
        [KeyboardButton(text=t["btn_ad"]), KeyboardButton(text=t["btn_earn"])],
        [KeyboardButton(text=t["btn_admin"])]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
