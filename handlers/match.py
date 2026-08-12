from datetime import datetime
from aiogram import Router, F, Bot
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from texts.loader import load
from models.user import User
from models.profile import Profile
from models.match import MatchRequest, ChatSession
from models.transaction import Transaction
from states.match import MatchForm
from config import REQUEST_FEE_UZS, CHAT_LIFETIME_DAYS

t_menu = load("uz", "menu")
t_match = load("uz", "match")
t_prof = load("uz", "profile")

router = Router()

def is_vip(user: User) -> bool:
    return bool(user.vip_expires_at and user.vip_expires_at > datetime.now(user.vip_expires_at.tzinfo))

async def process_match_request(message: Message, session: AsyncSession, bot: Bot, sender: User, target_profile: Profile) -> bool:
    # Validation
    if sender.id == target_profile.user_id:
        await message.answer(t_match["own_anketa_error"])
        return False
        
    sender_profile = await session.scalar(select(Profile).where(Profile.user_id == sender.id))
    if not sender_profile:
        await message.answer("Avval o'z profilingizni to'ldirishingiz kerak.")
        return False
        
    if sender_profile.gender == target_profile.gender:
        await message.answer(t_match["gender_error"])
        return False
        
    # Check if request already exists
    existing = await session.scalar(
        select(MatchRequest).where(
            MatchRequest.sender_id == sender.id,
            MatchRequest.receiver_id == target_profile.user_id
        )
    )
    if existing:
        await message.answer(t_match["already_sent"].format(status=existing.status))
        return False
        
    # Payment
    vip = is_vip(sender)
    fee = 0 if vip else REQUEST_FEE_UZS
    
    if sender.balance < fee:
        await message.answer(t_match["not_enough_balance"].format(
            price=f"{REQUEST_FEE_UZS:,}",
            balance=f"{sender.balance:,}"
        ))
        return False
        
    if fee > 0:
        before = sender.balance
        sender.balance -= fee
        tx = Transaction(
            user_id=sender.id,
            amount=-fee,
            type="match_request",
            description=f"{target_profile.anketa_number} ga so'rov",
            before_balance=before,
            after_balance=sender.balance
        )
        session.add(tx)
        
    req = MatchRequest(
        sender_id=sender.id,
        receiver_id=target_profile.user_id,
        status="pending",
        fee_paid=(fee > 0),
        fee_amount=fee
    )
    session.add(req)
    await session.commit()
    
    # Notify receiver
    target_user = await session.scalar(select(User).where(User.id == target_profile.user_id))
    if target_user:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=t_match["btn_accept"], callback_data=f"match_accept_{req.id}"),
                InlineKeyboardButton(text=t_match["btn_reject"], callback_data=f"match_reject_{req.id}")
            ]
        ])
        notify_text = t_match["new_request_notify"].format(
            anketa=sender_profile.anketa_number,
            gender=sender_profile.gender,
            age=sender_profile.age,
            height=sender_profile.height,
            weight=sender_profile.weight,
            location=sender_profile.location,
            bio=sender_profile.bio
        )
        try:
            await bot.send_message(target_user.telegram_id, notify_text, reply_markup=kb)
        except Exception:
            pass
            
    await message.answer(t_match["request_sent"])
    return True

@router.message(F.text == t_menu["btn_request"])
async def show_request_menu(message: Message, state: FSMContext):
    await state.set_state(MatchForm.anketa_number)
    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=t_menu["btn_main_menu"])]], resize_keyboard=True)
    await message.answer(t_match["ask_anketa_number"], reply_markup=kb)

@router.message(MatchForm.anketa_number)
async def process_anketa_number(message: Message, state: FSMContext, session: AsyncSession, bot: Bot):
    if message.text == t_menu["btn_main_menu"]:
        await state.clear()
        from keyboards.main import get_main_menu_kb
        await message.answer("Bosh menyu", reply_markup=get_main_menu_kb())
        return
        
    user = await session.scalar(select(User).where(User.telegram_id == message.from_user.id))
    if not user: return
    
    anketa_no = message.text.strip().upper()
    if not anketa_no.startswith("#"):
        anketa_no = "#" + anketa_no
        
    target_profile = await session.scalar(select(Profile).where(Profile.anketa_number == anketa_no, Profile.is_active == True))
    if not target_profile:
        await message.answer(t_match["anketa_not_found"])
        return
        
    success = await process_match_request(message, session, bot, user, target_profile)
    if success:
        await state.clear()
        from keyboards.main import get_main_menu_kb
        await message.answer("Bosh menyu", reply_markup=get_main_menu_kb())

@router.callback_query(F.data.startswith("match_"))
async def process_match_callback(callback: CallbackQuery, session: AsyncSession, bot: Bot):
    user = await session.scalar(select(User).where(User.telegram_id == callback.from_user.id))
    if not user: return
    
    parts = callback.data.split("_")
    action = parts[1]
    req_id = int(parts[2])
    
    req = await session.scalar(select(MatchRequest).where(MatchRequest.id == req_id))
    if not req or req.status != "pending" or req.receiver_id != user.id:
        await callback.answer("Bu so'rov eskirgan yoki noto'g'ri.", show_alert=True)
        return
        
    sender = await session.scalar(select(User).where(User.id == req.sender_id))
    receiver_profile = await session.scalar(select(Profile).where(Profile.user_id == req.receiver_id))
    
    if action == "reject":
        req.status = "rejected"
        if req.fee_paid and req.fee_amount > 0 and sender:
            before = sender.balance
            sender.balance += req.fee_amount
            tx = Transaction(
                user_id=sender.id,
                amount=req.fee_amount,
                type="match_refund",
                description="Rad etilgan so'rov uchun qaytarildi",
                before_balance=before,
                after_balance=sender.balance
            )
            session.add(tx)
        await session.commit()
        await callback.message.edit_text(callback.message.text + "\n\n❌ Rad etildi.")
        if sender:
            try:
                await bot.send_message(sender.telegram_id, t_match["notify_rejected"].format(anketa=receiver_profile.anketa_number))
            except Exception:
                pass
                
    elif action == "accept":
        req.status = "accepted"
        from datetime import timedelta
        expires = datetime.now() + timedelta(days=CHAT_LIFETIME_DAYS)
        
        chat = ChatSession(
            match_request_id=req.id,
            user1_id=req.sender_id,
            user2_id=req.receiver_id,
            expires_at=expires
        )
        session.add(chat)
        await session.commit()
        await callback.message.edit_text(callback.message.text + "\n\n✅ Qabul qilindi.")
        
        instructions = t_match["chat_instructions"].format(days=CHAT_LIFETIME_DAYS)
        await bot.send_message(callback.from_user.id, instructions)
        if sender:
            try:
                await bot.send_message(sender.telegram_id, t_match["notify_accepted"].format(anketa=receiver_profile.anketa_number))
                await bot.send_message(sender.telegram_id, instructions)
            except Exception:
                pass
                
@router.message(F.text == t_menu["btn_new_requests"])
async def show_new_requests(message: Message, session: AsyncSession, bot: Bot):
    user = await session.scalar(select(User).where(User.telegram_id == message.from_user.id))
    if not user: return
    
    stmt = select(MatchRequest).where(MatchRequest.receiver_id == user.id, MatchRequest.status == "pending")
    result = await session.execute(stmt)
    reqs = result.scalars().all()
    
    if not reqs:
        await message.answer("Sizda yangi so'rovlar yo'q.")
        return
        
    await message.answer(f"Sizda {len(reqs)} ta yangi so'rov mavjud. Ular sizga bildirishnoma orqali yuborilgan. Tarixga qarang.")
