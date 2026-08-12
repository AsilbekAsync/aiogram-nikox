from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from models.user import User
from models.profile import Profile
from models.transaction import Transaction
from config import ADMIN_IDS

router = Router()

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

@router.message(Command("stats"))
async def show_stats(message: Message, session: AsyncSession):
    if not is_admin(message.from_user.id):
        return
        
    users_count = await session.scalar(select(func.count(User.id)))
    profiles_count = await session.scalar(select(func.count(Profile.id)))
    active_profiles_count = await session.scalar(select(func.count(Profile.id)).where(Profile.is_active == True))
    
    total_balance = await session.scalar(select(func.sum(User.balance)))
    
    text = (
        "📊 Bot Statistikasi:\n\n"
        f"👥 Umumiy foydalanuvchilar: {users_count}\n"
        f"📝 Umumiy anketalar: {profiles_count}\n"
        f"✅ Faol anketalar: {active_profiles_count}\n"
        f"💰 Tizimdagi umumiy balans: {total_balance or 0:,} so'm\n"
    )
    await message.answer(text)

@router.message(Command("approve"))
async def approve_deposit(message: Message, session: AsyncSession):
    if not is_admin(message.from_user.id):
        return
        
    parts = message.text.split()
    if len(parts) != 3:
        await message.answer("Format: /approve <telegram_id> <summa>")
        return
        
    try:
        tg_id = int(parts[1])
        amount = int(parts[2])
    except ValueError:
        await message.answer("Xato! ID va Summa raqam bo'lishi kerak.")
        return
        
    user = await session.scalar(select(User).where(User.telegram_id == tg_id))
    if not user:
        await message.answer("Foydalanuvchi topilmadi.")
        return
        
    before = user.balance
    user.balance += amount
    
    tx = Transaction(
        user_id=user.id,
        amount=amount,
        type="topup",
        description="Admin tomonidan balans to'ldirildi (Chek tasdiqlandi)",
        before_balance=before,
        after_balance=user.balance
    )
    session.add(tx)
    await session.commit()
    
    await message.answer(f"✅ {tg_id} balansiga {amount:,} so'm qo'shildi.")
    
    try:
        await message.bot.send_message(tg_id, f"✅ To'lov cheki tasdiqlandi!\nBalansingizga {amount:,} so'm qo'shildi.")
    except Exception:
        pass

@router.message(Command("reject"))
async def reject_deposit(message: Message, session: AsyncSession):
    if not is_admin(message.from_user.id):
        return
        
    parts = message.text.split()
    if len(parts) != 2:
        await message.answer("Format: /reject <telegram_id>")
        return
        
    try:
        tg_id = int(parts[1])
    except ValueError:
        await message.answer("Xato! ID raqam bo'lishi kerak.")
        return
        
    await message.answer(f"❌ {tg_id} to'lovi rad etildi.")
    
    try:
        await message.bot.send_message(tg_id, "❌ To'lov chekingiz rad etildi. Sababini bilish uchun adminga murojaat qiling.")
    except Exception:
        pass
