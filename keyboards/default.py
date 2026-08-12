from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from texts.loader import load

labels = load("uz", "labels")


def main_menu() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text=labels["main_menu"]))
    builder.add(KeyboardButton(text=labels["settings"]))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)
