from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from sqlalchemy.ext.asyncio import AsyncSession

from texts.loader import load
from services.user import get_user_by_tg_id
from services.wallet import verify_phone_and_give_bonus
from config import WELCOME_BONUS_UZS

t = load("uz")
router = Router()

@router.message(F.contact)
async def contact_handler(message: Message, session: AsyncSession):
    assert message.from_user is not None
    assert message.contact is not None
    
    # Check if contact belongs to the user
    if message.contact.user_id != message.from_user.id:
        # User sent someone else's contact
        await message.answer("Iltimos, o'zingizning telefon raqamingizni yuboring.")
        return
        
    user = await get_user_by_tg_id(session, message.from_user.id)
    if not user:
        return
        
    if user.status != "unverified_phone":
        await message.answer("Raqamingiz allaqachon tasdiqlangan.", reply_markup=ReplyKeyboardRemove())
        return
        
    await verify_phone_and_give_bonus(session, user, message.contact.phone_number)
    
    # Send welcome verified message
    msg_text = t["welcome_verified"].format(bonus=WELCOME_BONUS_UZS)
    
    from keyboards.main import get_main_menu_kb
    await message.answer(msg_text, reply_markup=get_main_menu_kb())
