from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from texts.loader import load
from models.user import User
from models.transaction import Transaction
from config import ADMIN_IDS

t_menu = load("uz", "menu")
t_wallet = load("uz", "wallet")

router = Router()

class DepositForm(StatesGroup):
    waiting_for_receipt = State()

@router.message(F.text == t_menu["btn_wallet"])
async def show_wallet(message: Message, session: AsyncSession):
    user = await session.scalar(select(User).where(User.telegram_id == message.from_user.id))
    if not user: return
    
    text = t_wallet["wallet_info"].format(balance=f"{user.balance:,}")
    await message.answer(text)

@router.message(F.text == t_menu["btn_history"])
async def show_history(message: Message, session: AsyncSession):
    user = await session.scalar(select(User).where(User.telegram_id == message.from_user.id))
    if not user: return
    
    stmt = select(Transaction).where(Transaction.user_id == user.id).order_by(Transaction.created_at.desc()).limit(10)
    result = await session.execute(stmt)
    txs = result.scalars().all()
    
    if not txs:
        await message.answer(t_wallet["history_empty"])
        return
        
    text = t_wallet["history_header"]
    for tx in txs:
        date_str = tx.created_at.strftime("%Y-%m-%d %H:%M:%S")
        text += t_wallet["history_item"].format(
            date=date_str,
            amount=f"{tx.amount:,}",
            type=tx.type,
            desc=tx.description or ""
        )
    
    await message.answer(text)

@router.message(F.text == t_menu["btn_deposit"])
async def show_deposit_options(message: Message):
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t_wallet["btn_uzcard"])], [KeyboardButton(text=t_menu["btn_main_menu"])]],
        resize_keyboard=True
    )
    await message.answer(t_wallet["deposit_info"], reply_markup=kb)

@router.message(F.text == t_wallet["btn_uzcard"])
async def deposit_uzcard(message: Message, state: FSMContext):
    # Fetch from env in real app, hardcoded here per TASK
    min_deposit = 50000
    text = t_wallet["deposit_uzcard_instructions"].format(min_deposit=f"{min_deposit:,}")
    
    from keyboards.main import get_main_menu_kb
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t_menu["btn_main_menu"])]],
        resize_keyboard=True
    )
    
    await state.set_state(DepositForm.waiting_for_receipt)
    await message.answer(text, reply_markup=kb)

@router.message(DepositForm.waiting_for_receipt, F.photo)
async def process_receipt(message: Message, state: FSMContext, session: AsyncSession):
    user = await session.scalar(select(User).where(User.telegram_id == message.from_user.id))
    
    # In a real app we'd save this to DB and notify admin
    photo = message.photo[-1].file_id
    text = f"yangi to'lov cheki keldi!\nFoydalanuvchi: {message.from_user.full_name} ({message.from_user.id})"
    
    # Send to admins
    for admin_id in ADMIN_IDS:
        try:
            await message.bot.send_photo(admin_id, photo, caption=text)
        except Exception:
            pass
            
    await state.clear()
    from keyboards.main import get_main_menu_kb
    await message.answer(t_wallet["receipt_received"], reply_markup=get_main_menu_kb())

@router.message(F.text == t_menu["btn_main_menu"])
async def return_to_main_menu(message: Message, state: FSMContext):
    await state.clear()
    from keyboards.main import get_main_menu_kb
    await message.answer("Bosh menyu", reply_markup=get_main_menu_kb())

@router.message(F.text == t_menu["btn_earn"])
async def earn_money(message: Message, session: AsyncSession):
    user = await session.scalar(select(User).where(User.telegram_id == message.from_user.id))
    if not user: return
    
    from models.referral import Referral
    from config import REFERRAL_BONUS_UZS
    
    stmt = select(func.count(Referral.id)).where(Referral.inviter_id == user.id, Referral.status == "completed")
    count_res = await session.execute(stmt)
    count = count_res.scalar() or 0
    
    stmt_sum = select(func.sum(Referral.reward_amount)).where(Referral.inviter_id == user.id, Referral.status == "completed")
    sum_res = await session.execute(stmt_sum)
    total_earned = sum_res.scalar() or 0
    
    me = await message.bot.get_me()
    
    text = t_wallet["earn_info"].format(
        bonus=f"{REFERRAL_BONUS_UZS:,}",
        bot_username=me.username,
        referral_code=user.referral_code,
        count=count,
        total_earned=f"{int(total_earned):,}"
    )
    
    await message.answer(text)

