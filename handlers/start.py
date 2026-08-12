from aiogram import Router
from aiogram.filters import CommandStart, CommandObject, StateFilter, Command
from aiogram.fsm.state import any_state
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from texts.loader import load
from services.user import get_user_by_tg_id, create_user, get_user_by_referral_code, register_referral

t = load("uz")
router = Router()

@router.message(CommandStart(), StateFilter(any_state))
async def start_cmd(message: Message, command: CommandObject, session: AsyncSession, state: FSMContext):
    await state.clear()
    assert message.from_user is not None
    tg_id = message.from_user.id
    
    user = await get_user_by_tg_id(session, tg_id)
    referral_code = command.args
    
    if not user:
        user = await create_user(session, tg_id, message.from_user.full_name, message.from_user.username)
        if referral_code:
            inviter = await get_user_by_referral_code(session, referral_code)
            if inviter and inviter.id != user.id:
                await register_referral(session, inviter.id, user.id)
                
    if user.status == "unverified_phone":
        kb = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text=t["btn_send_contact"], request_contact=True)]],
            resize_keyboard=True
        )
        await message.answer(t["start_unverified"], reply_markup=kb)
    else:
        from keyboards.main import get_main_menu_kb
        await message.answer(t["welcome_back"].format(full_name=user.full_name), reply_markup=get_main_menu_kb())

@router.message(Command("cancel"), StateFilter(any_state))
async def cancel_cmd(message: Message, state: FSMContext):
    await state.clear()
    from keyboards.main import get_main_menu_kb
    await message.answer("Barcha amallar bekor qilindi.", reply_markup=get_main_menu_kb())
