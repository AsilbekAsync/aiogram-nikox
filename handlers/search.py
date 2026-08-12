from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from texts.loader import load
from models.user import User
from models.profile import Profile
from models.transaction import Transaction
from states.search import SearchForm
from config import SEARCH_ACCESS_FEE_UZS
from utils.validators import validate_age

t_menu = load("uz", "menu")
t_search = load("uz", "search")
t_prof = load("uz", "profile")

router = Router()

def is_vip(user: User) -> bool:
    return bool(user.vip_expires_at and user.vip_expires_at > datetime.now(user.vip_expires_at.tzinfo))

def has_search_access(user: User) -> bool:
    return user.search_access or is_vip(user)

def get_search_start_kb(has_access: bool):
    if has_access:
        return ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="🔍 Qidirishni boshlash")], [KeyboardButton(text=t_menu["btn_main_menu"])]],
            resize_keyboard=True
        )
    else:
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text=t_search["btn_buy_access"].format(price=f"{SEARCH_ACCESS_FEE_UZS:,}"))],
                [KeyboardButton(text=t_menu["btn_main_menu"])]
            ],
            resize_keyboard=True
        )

@router.message(F.text == t_menu["btn_search"])
async def show_search(message: Message, session: AsyncSession, state: FSMContext):
    await state.clear()
    user = await session.scalar(select(User).where(User.telegram_id == message.from_user.id))
    if not user: return
    
    access = has_search_access(user)
    status_text = t_search["access_granted"] if access else t_search["access_denied"]
    
    text = t_search["search_info"].format(
        price=f"{SEARCH_ACCESS_FEE_UZS:,}",
        access_status=status_text
    )
    await message.answer(text, reply_markup=get_search_start_kb(access))

@router.message(F.text.startswith("🔓 Qidiruvni faollashtirish"))
async def buy_search_access(message: Message, session: AsyncSession, state: FSMContext):
    user = await session.scalar(select(User).where(User.telegram_id == message.from_user.id))
    if not user: return
    
    if user.balance < SEARCH_ACCESS_FEE_UZS:
        await message.answer(t_search["not_enough_balance"].format(
            balance=f"{user.balance:,}",
            price=f"{SEARCH_ACCESS_FEE_UZS:,}"
        ))
        return
        
    before_balance = user.balance
    after_balance = before_balance - SEARCH_ACCESS_FEE_UZS
    user.balance = after_balance
    user.search_access = True
    
    tx = Transaction(
        user_id=user.id,
        amount=-SEARCH_ACCESS_FEE_UZS,
        type="search_access",
        description="Anketa qidirish uchun to'lov",
        before_balance=before_balance,
        after_balance=after_balance
    )
    session.add(tx)
    await session.commit()
    
    await message.answer(t_search["access_success"], reply_markup=get_search_start_kb(True))

@router.message(F.text == "🔍 Qidirishni boshlash")
async def start_search_flow(message: Message, session: AsyncSession, state: FSMContext):
    user = await session.scalar(select(User).where(User.telegram_id == message.from_user.id))
    if not user or not has_search_access(user):
        return
        
    await state.set_state(SearchForm.gender)
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t_prof["btn_male"]), KeyboardButton(text=t_prof["btn_female"])]],
        resize_keyboard=True
    )
    await message.answer(t_search["ask_search_gender"], reply_markup=kb)

@router.message(SearchForm.gender)
async def search_process_gender(message: Message, state: FSMContext):
    gender = "erkak" if message.text == t_prof["btn_male"] else "ayol" if message.text == t_prof["btn_female"] else None
    if not gender:
        return
    await state.update_data(gender=gender)
    await state.set_state(SearchForm.age_min)
    await message.answer(t_search["ask_search_age_min"], reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=t_menu["btn_main_menu"])]], resize_keyboard=True))

@router.message(SearchForm.age_min)
async def search_process_age_min(message: Message, state: FSMContext):
    if message.text == t_menu["btn_main_menu"]:
        await state.clear()
        from keyboards.main import get_main_menu_kb
        await message.answer("Bosh menyu", reply_markup=get_main_menu_kb())
        return
        
    age = validate_age(message.text)
    if age is None:
        await message.answer(t_prof["err_age"])
        return
    await state.update_data(age_min=age)
    await state.set_state(SearchForm.age_max)
    await message.answer(t_search["ask_search_age_max"])

@router.message(SearchForm.age_max)
async def search_process_age_max(message: Message, state: FSMContext, session: AsyncSession):
    if message.text == t_menu["btn_main_menu"]:
        await state.clear()
        from keyboards.main import get_main_menu_kb
        await message.answer("Bosh menyu", reply_markup=get_main_menu_kb())
        return
        
    age = validate_age(message.text)
    if age is None:
        await message.answer(t_prof["err_age"])
        return
    await state.update_data(age_max=age)
    
    # Perform search
    data = await state.get_data()
    stmt = select(Profile.id).where(
        Profile.gender == data["gender"],
        Profile.age >= data["age_min"],
        Profile.age <= data["age_max"],
        Profile.visibility != "private",
        Profile.is_active == True
    )
    result = await session.execute(stmt)
    profile_ids = result.scalars().all()
    
    if not profile_ids:
        await state.clear()
        from keyboards.main import get_main_menu_kb
        await message.answer(t_search["search_no_results"], reply_markup=get_main_menu_kb())
        return
        
    await state.update_data(profile_ids=list(profile_ids), current_idx=0)
    await message.answer(t_search["search_results"].format(count=len(profile_ids)))
    await show_profile(message, state, session)

async def show_profile(message: Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    profile_ids = data.get("profile_ids", [])
    idx = data.get("current_idx", 0)
    
    if not profile_ids or idx >= len(profile_ids) or idx < 0:
        return
        
    profile_id = profile_ids[idx]
    profile = await session.scalar(select(Profile).where(Profile.id == profile_id))
    if not profile:
        return
        
    # Render profile
    text = t_prof["preview_template"].format(
        anketa=profile.anketa_number,
        gender=profile.gender,
        age=profile.age,
        height=profile.height,
        weight=profile.weight,
        nationality=profile.nationality,
        marital_status=profile.marital_status,
        location=profile.location,
        original_location=profile.original_location,
        religion=profile.religion,
        languages_count=profile.languages_count,
        bio=profile.bio,
        partner_requirements=profile.partner_requirements,
        filled_by=profile.filled_by
    )
    
    if profile.gender == "ayol":
        text += "\n" + t_prof["preview_template_female"].format(
            children_count=profile.children_count or 0,
            hijab="Ha" if profile.hijab else "Yo'q",
            relocation="Ha" if profile.relocation else "Yo'q",
            second_wife="Ha" if profile.second_wife else "Yo'q"
        )
        
    # Keyboard
    buttons = []
    nav_row = []
    if idx > 0:
        nav_row.append(KeyboardButton(text=t_search["btn_prev"]))
    if idx < len(profile_ids) - 1:
        nav_row.append(KeyboardButton(text=t_search["btn_next"]))
        
    if nav_row:
        buttons.append(nav_row)
        
    buttons.append([KeyboardButton(text=t_search["btn_request"])])
    buttons.append([KeyboardButton(text=t_menu["btn_main_menu"])])
    
    await state.set_state(SearchForm.viewing)
    await message.answer(text, reply_markup=ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True))

@router.message(SearchForm.viewing)
async def process_viewing(message: Message, state: FSMContext, session: AsyncSession):
    if message.text == t_menu["btn_main_menu"]:
        await state.clear()
        from keyboards.main import get_main_menu_kb
        await message.answer("Bosh menyu", reply_markup=get_main_menu_kb())
        return
        
    data = await state.get_data()
    idx = data.get("current_idx", 0)
    
    if message.text == t_search["btn_next"]:
        await state.update_data(current_idx=idx + 1)
        await show_profile(message, state, session)
    elif message.text == t_search["btn_prev"]:
        await state.update_data(current_idx=idx - 1)
        await show_profile(message, state, session)
    elif message.text == t_search["btn_request"]:
        from handlers.match import process_match_request
        target_profile = await session.scalar(select(Profile).where(Profile.id == profile_ids[idx]))
        user = await session.scalar(select(User).where(User.telegram_id == message.from_user.id))
        
        if target_profile and user:
            await process_match_request(message, session, message.bot, user, target_profile)

@router.message(F.text == t_menu["btn_hidden"])
async def show_hidden(message: Message, session: AsyncSession):
    user = await session.scalar(select(User).where(User.telegram_id == message.from_user.id))
    if not user: return
    
    if not has_search_access(user):
        kb = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text=t_search["btn_buy_access"].format(price=f"{SEARCH_ACCESS_FEE_UZS:,}"))],
                [KeyboardButton(text=t_menu["btn_main_menu"])]
            ],
            resize_keyboard=True
        )
        await message.answer("Yashirin anketalarni ko'rish uchun qidiruv ruxsatini sotib oling yoki VIP bo'ling.", reply_markup=kb)
        return
        
    await message.answer("🕵️ Yashirin anketalar bo'limi ustida ish olib borilmoqda. Tez kunda ishga tushadi!")

@router.message(F.text == t_menu["btn_ad"])
async def show_ad_info(message: Message):
    await message.answer("📢 Kanalda e'lon berish bo'yicha adminga murojaat qiling: @admin_username")

