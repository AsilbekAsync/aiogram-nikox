from aiogram import Router
from aiogram.types import Message

from texts.loader import load

t = load("uz")
router = Router()


@router.message()
async def unknown_cmd(message: Message):
    await message.answer(t["unknown"])
