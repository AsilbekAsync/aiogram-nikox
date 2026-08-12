from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from texts.loader import load

t = load("uz")
router = Router()


@router.message(CommandStart())
async def start_cmd(message: Message):
    assert message.from_user is not None
    await message.answer(
        t["start"].format(full_name=message.from_user.full_name)
    )
