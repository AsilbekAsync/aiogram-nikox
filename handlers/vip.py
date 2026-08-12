from datetime import datetime, timedelta
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from texts.loader import load
from models.user import User
from models.transaction import Transaction
from config import VIP_1_DAY_UZS, VIP_1_WEEK_UZS, VIP_1_MONTH_UZS

t_menu = load("uz", "menu")
t_vip = load("uz", "vip")

router = Router()

def get_vip_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t_vip["btn_vip_1_day"].format(price=f"{VIP_1_DAY_UZS:,}"))],
            [KeyboardButton(text=t_vip["btn_vip_1_week"].format(price=f"{VIP_1_WEEK_UZS:,}"))],
            [KeyboardButton(text=t_vip["btn_vip_1_month"].format(price=f"{VIP_1_MONTH_UZS:,}"))],
            [KeyboardButton(text=t_menu["btn_main_menu"])]
        ],
        resize_keyboard=True
    )

@router.message(F.text == t_menu["btn_vip"])
async def show_vip(message: Message, session: AsyncSession):
    user = await session.scalar(select(User).where(User.telegram_id == message.from_user.id))
    if not user: return
    
    if user.vip_expires_at and user.vip_expires_at > datetime.now(user.vip_expires_at.tzinfo):
        status = t_vip["vip_active"].format(expires_at=user.vip_expires_at.strftime("%Y-%m-%d %H:%M:%S"))
    else:
        status = t_vip["vip_inactive"]
        
    text = t_vip["vip_info"].format(status=status)
    await message.answer(text, reply_markup=get_vip_kb())

async def process_vip_purchase(message: Message, session: AsyncSession, duration_days: int, price: int):
    user = await session.scalar(select(User).where(User.telegram_id == message.from_user.id))
    if not user: return
    
    if user.balance < price:
        text = t_vip["not_enough_balance"].format(
            balance=f"{user.balance:,}",
            price=f"{price:,}"
        )
        await message.answer(text)
        return
        
    # Process purchase
    before_balance = user.balance
    after_balance = before_balance - price
    user.balance = after_balance
    
    # Update VIP expiration
    now = datetime.now()
    if user.vip_expires_at and user.vip_expires_at > now.astimezone(user.vip_expires_at.tzinfo):
        user.vip_expires_at = user.vip_expires_at + timedelta(days=duration_days)
    else:
        user.vip_expires_at = now + timedelta(days=duration_days)
        
    # Transaction
    tx = Transaction(
        user_id=user.id,
        amount=-price,
        type="vip_purchase",
        description=f"VIP sotib olish ({duration_days} kun)",
        before_balance=before_balance,
        after_balance=after_balance
    )
    session.add(tx)
    await session.commit()
    
    from keyboards.main import get_main_menu_kb
    await message.answer(t_vip["vip_success"], reply_markup=get_main_menu_kb())

@router.message(F.text.startswith("1 kunlik"))
async def buy_vip_1_day(message: Message, session: AsyncSession):
    await process_vip_purchase(message, session, 1, VIP_1_DAY_UZS)

@router.message(F.text.startswith("1 haftalik"))
async def buy_vip_1_week(message: Message, session: AsyncSession):
    await process_vip_purchase(message, session, 7, VIP_1_WEEK_UZS)

@router.message(F.text.startswith("1 oylik"))
async def buy_vip_1_month(message: Message, session: AsyncSession):
    await process_vip_purchase(message, session, 30, VIP_1_MONTH_UZS)
