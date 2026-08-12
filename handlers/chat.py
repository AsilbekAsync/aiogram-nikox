from datetime import datetime
from aiogram import Router, F, Bot
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from texts.loader import load
from models.user import User
from models.profile import Profile
from models.match import ChatSession
from states.chat import ChatForm

t_menu = load("uz", "menu")
t_chat = load("uz", "chat")

router = Router()

@router.message(F.text == t_menu["btn_chats"])
async def show_chats(message: Message, session: AsyncSession, state: FSMContext):
    user = await session.scalar(select(User).where(User.telegram_id == message.from_user.id))
    if not user: return
    
    stmt = select(ChatSession).where(
        or_(ChatSession.user1_id == user.id, ChatSession.user2_id == user.id),
        ChatSession.is_active == True,
        ChatSession.expires_at > datetime.now()
    )
    result = await session.execute(stmt)
    chats = result.scalars().all()
    
    if not chats:
        await message.answer(t_chat["no_chats"])
        return
        
    buttons = []
    for chat in chats:
        other_user_id = chat.user2_id if chat.user1_id == user.id else chat.user1_id
        other_profile = await session.scalar(select(Profile).where(Profile.user_id == other_user_id))
        
        if other_profile:
            buttons.append([KeyboardButton(text=f"Chat: {other_profile.anketa_number}")])
            
    buttons.append([KeyboardButton(text=t_menu["btn_main_menu"])])
    kb = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    
    await message.answer(t_chat["chat_list"], reply_markup=kb)

@router.message(F.text.startswith("Chat: #"))
async def enter_chat(message: Message, session: AsyncSession, state: FSMContext):
    user = await session.scalar(select(User).where(User.telegram_id == message.from_user.id))
    if not user: return
    
    target_anketa = message.text.split(" ")[1]
    target_profile = await session.scalar(select(Profile).where(Profile.anketa_number == target_anketa))
    if not target_profile: return
    
    # Verify chat exists
    stmt = select(ChatSession).where(
        or_(
            (ChatSession.user1_id == user.id) & (ChatSession.user2_id == target_profile.user_id),
            (ChatSession.user1_id == target_profile.user_id) & (ChatSession.user2_id == user.id)
        ),
        ChatSession.is_active == True,
        ChatSession.expires_at > datetime.now()
    )
    result = await session.execute(stmt)
    chat = result.scalar_one_or_none()
    
    if not chat:
        await message.answer(t_chat["no_chats"])
        return
        
    await state.set_state(ChatForm.active_chat)
    await state.update_data(chat_id=chat.id, target_user_id=target_profile.user_id, target_anketa=target_anketa)
    
    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=t_chat["btn_back"])]], resize_keyboard=True)
    await message.answer(t_chat["chat_joined"].format(anketa=target_anketa), reply_markup=kb)

@router.message(ChatForm.active_chat)
async def process_chat_message(message: Message, session: AsyncSession, state: FSMContext, bot: Bot):
    if message.text == t_chat["btn_back"]:
        await state.clear()
        from keyboards.main import get_main_menu_kb
        await message.answer(t_chat["chat_left"], reply_markup=get_main_menu_kb())
        return
        
    data = await state.get_data()
    chat_id = data.get("chat_id")
    target_user_id = data.get("target_user_id")
    
    if not chat_id or not target_user_id:
        return
        
    chat = await session.scalar(select(ChatSession).where(ChatSession.id == chat_id, ChatSession.is_active == True, ChatSession.expires_at > datetime.now()))
    if not chat:
        await message.answer(t_chat["msg_not_sent"])
        await state.clear()
        from keyboards.main import get_main_menu_kb
        await message.answer(t_chat["chat_left"], reply_markup=get_main_menu_kb())
        return
        
    target_user = await session.scalar(select(User).where(User.id == target_user_id))
    sender_profile = await session.scalar(select(Profile).where(Profile.user_id == chat.user1_id if chat.user1_id != target_user_id else chat.user2_id))
    
    if not target_user or not sender_profile:
        return
        
    anketa = sender_profile.anketa_number
    
    try:
        # We prepend a notification text if it's a text message, otherwise just copy
        if message.text:
            await bot.send_message(target_user.telegram_id, t_chat["msg_forwarded_from"].format(anketa=anketa) + message.text)
        else:
            await bot.send_message(target_user.telegram_id, t_chat["msg_forwarded_from"].format(anketa=anketa))
            await message.copy_to(target_user.telegram_id)
    except Exception:
        pass
