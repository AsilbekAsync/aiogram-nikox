import uuid
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from texts.loader import load
from states.profile import ProfileForm
from models.user import User
from models.profile import Profile
from utils.validators import validate_age, validate_height, validate_weight, validate_languages, validate_children, parse_boolean

t_menu = load("uz", "menu")
t_prof = load("uz", "profile")

router = Router()

def get_gender_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t_prof["btn_male"]), KeyboardButton(text=t_prof["btn_female"])]],
        resize_keyboard=True
    )

def get_cancel_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t_prof["btn_cancel"])]],
        resize_keyboard=True
    )

def get_yes_no_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Ha"), KeyboardButton(text="Yo'q")], [KeyboardButton(text=t_prof["btn_cancel"])]],
        resize_keyboard=True
    )

def get_filled_by_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="O'zim"), KeyboardButton(text="Vakilim")], [KeyboardButton(text=t_prof["btn_cancel"])]],
        resize_keyboard=True
    )

def get_confirm_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t_prof["btn_confirm"]), KeyboardButton(text=t_prof["btn_restart"])]],
        resize_keyboard=True
    )

@router.message(F.text == t_menu["btn_profile"])
async def start_profile(message: Message, state: FSMContext, session: AsyncSession):
    # Verify user is ready
    user = await session.scalar(select(User).where(User.telegram_id == message.from_user.id))
    if not user or user.status == "unverified_phone":
        await message.answer("Avval telefon raqamingizni tasdiqlang.")
        return
        
    await state.set_state(ProfileForm.gender)
    await message.answer(t_prof["ask_gender"], reply_markup=get_gender_kb())

@router.message(F.text == t_prof["btn_cancel"])
async def cancel_profile(message: Message, state: FSMContext):
    await state.clear()
    from keyboards.main import get_main_menu_kb
    await message.answer("Bekor qilindi.", reply_markup=get_main_menu_kb())

@router.message(ProfileForm.gender)
async def process_gender(message: Message, state: FSMContext):
    gender = "erkak" if message.text == t_prof["btn_male"] else "ayol" if message.text == t_prof["btn_female"] else None
    if not gender:
        await message.answer(t_prof["ask_gender"], reply_markup=get_gender_kb())
        return
    await state.update_data(gender=gender)
    await state.set_state(ProfileForm.age)
    await message.answer(t_prof["ask_age"], reply_markup=get_cancel_kb())

@router.message(ProfileForm.age)
async def process_age(message: Message, state: FSMContext):
    age = validate_age(message.text)
    if age is None:
        await message.answer(t_prof["err_age"])
        return
    await state.update_data(age=age)
    await state.set_state(ProfileForm.height)
    await message.answer(t_prof["ask_height"])

@router.message(ProfileForm.height)
async def process_height(message: Message, state: FSMContext):
    height = validate_height(message.text)
    if height is None:
        await message.answer(t_prof["err_height"])
        return
    await state.update_data(height=height)
    await state.set_state(ProfileForm.weight)
    await message.answer(t_prof["ask_weight"])

@router.message(ProfileForm.weight)
async def process_weight(message: Message, state: FSMContext):
    weight = validate_weight(message.text)
    if weight is None:
        await message.answer(t_prof["err_weight"])
        return
    await state.update_data(weight=weight)
    await state.set_state(ProfileForm.nationality)
    await message.answer(t_prof["ask_nationality"])

@router.message(ProfileForm.nationality)
async def process_nationality(message: Message, state: FSMContext):
    await state.update_data(nationality=message.text[:64])
    await state.set_state(ProfileForm.marital_status)
    await message.answer(t_prof["ask_marital_status"])

@router.message(ProfileForm.marital_status)
async def process_marital(message: Message, state: FSMContext):
    await state.update_data(marital_status=message.text[:64])
    await state.set_state(ProfileForm.location)
    await message.answer(t_prof["ask_location"])

@router.message(ProfileForm.location)
async def process_loc(message: Message, state: FSMContext):
    await state.update_data(location=message.text[:128])
    await state.set_state(ProfileForm.original_location)
    await message.answer(t_prof["ask_original_location"])

@router.message(ProfileForm.original_location)
async def process_orig_loc(message: Message, state: FSMContext):
    await state.update_data(original_location=message.text[:128])
    await state.set_state(ProfileForm.religion)
    await message.answer(t_prof["ask_religion"])

@router.message(ProfileForm.religion)
async def process_rel(message: Message, state: FSMContext):
    await state.update_data(religion=message.text[:128])
    await state.set_state(ProfileForm.languages_count)
    await message.answer(t_prof["ask_languages"])

@router.message(ProfileForm.languages_count)
async def process_langs(message: Message, state: FSMContext):
    langs = validate_languages(message.text)
    if langs is None:
        await message.answer(t_prof["err_langs"])
        return
    await state.update_data(languages_count=langs)
    await state.set_state(ProfileForm.bio)
    await message.answer(t_prof["ask_bio"])

@router.message(ProfileForm.bio)
async def process_bio(message: Message, state: FSMContext):
    await state.update_data(bio=message.text[:500])
    await state.set_state(ProfileForm.partner_requirements)
    await message.answer(t_prof["ask_partner"])

@router.message(ProfileForm.partner_requirements)
async def process_partner(message: Message, state: FSMContext):
    await state.update_data(partner_requirements=message.text[:500])
    await state.set_state(ProfileForm.filled_by)
    await message.answer(t_prof["ask_filled_by"], reply_markup=get_filled_by_kb())

@router.message(ProfileForm.filled_by)
async def process_filled_by(message: Message, state: FSMContext):
    data = await state.get_data()
    filled_by = message.text[:32]
    await state.update_data(filled_by=filled_by)
    
    if data.get("gender") == "ayol":
        await state.set_state(ProfileForm.children_count)
        await message.answer(t_prof["ask_children"], reply_markup=get_cancel_kb())
    else:
        await show_preview(message, state)

@router.message(ProfileForm.children_count)
async def process_children(message: Message, state: FSMContext):
    children = validate_children(message.text)
    if children is None:
        await message.answer(t_prof["err_children"])
        return
    await state.update_data(children_count=children)
    await state.set_state(ProfileForm.hijab)
    await message.answer(t_prof["ask_hijab"], reply_markup=get_yes_no_kb())

@router.message(ProfileForm.hijab)
async def process_hijab(message: Message, state: FSMContext):
    val = parse_boolean(message.text)
    if val is None:
        await message.answer(t_prof["ask_hijab"], reply_markup=get_yes_no_kb())
        return
    await state.update_data(hijab=val)
    await state.set_state(ProfileForm.relocation)
    await message.answer(t_prof["ask_relocation"], reply_markup=get_yes_no_kb())

@router.message(ProfileForm.relocation)
async def process_relocation(message: Message, state: FSMContext):
    val = parse_boolean(message.text)
    if val is None:
        await message.answer(t_prof["ask_relocation"], reply_markup=get_yes_no_kb())
        return
    await state.update_data(relocation=val)
    await state.set_state(ProfileForm.second_wife)
    await message.answer(t_prof["ask_second_wife"], reply_markup=get_yes_no_kb())

@router.message(ProfileForm.second_wife)
async def process_second_wife(message: Message, state: FSMContext):
    val = parse_boolean(message.text)
    if val is None:
        await message.answer(t_prof["ask_second_wife"], reply_markup=get_yes_no_kb())
        return
    await state.update_data(second_wife=val)
    await show_preview(message, state)

async def show_preview(message: Message, state: FSMContext):
    data = await state.get_data()
    anketa_no = f"#{str(uuid.uuid4().hex)[:6].upper()}"
    await state.update_data(anketa_number=anketa_no)
    
    text = t_prof["preview_header"] + "\n\n"
    text += t_prof["preview_template"].format(
        anketa=anketa_no,
        gender=data.get("gender", ""),
        age=data.get("age", ""),
        height=data.get("height", ""),
        weight=data.get("weight", ""),
        nationality=data.get("nationality", ""),
        marital_status=data.get("marital_status", ""),
        location=data.get("location", ""),
        original_location=data.get("original_location", ""),
        religion=data.get("religion", ""),
        languages_count=data.get("languages_count", ""),
        bio=data.get("bio", ""),
        partner_requirements=data.get("partner_requirements", ""),
        filled_by=data.get("filled_by", "")
    )
    
    if data.get("gender") == "ayol":
        text += "\n" + t_prof["preview_template_female"].format(
            children_count=data.get("children_count", ""),
            hijab="Ha" if data.get("hijab") else "Yo'q",
            relocation="Ha" if data.get("relocation") else "Yo'q",
            second_wife="Ha" if data.get("second_wife") else "Yo'q"
        )
        
    await state.set_state(ProfileForm.preview)
    await message.answer(text, reply_markup=get_confirm_kb())

@router.message(ProfileForm.preview)
async def process_preview(message: Message, state: FSMContext, session: AsyncSession):
    if message.text == t_prof["btn_restart"]:
        await state.set_state(ProfileForm.gender)
        await message.answer(t_prof["ask_gender"], reply_markup=get_gender_kb())
        return
        
    if message.text == t_prof["btn_confirm"]:
        data = await state.get_data()
        user = await session.scalar(select(User).where(User.telegram_id == message.from_user.id))
        
        # Check if profile already exists
        existing = await session.scalar(select(Profile).where(Profile.user_id == user.id))
        if existing:
            # Update existing
            for k, v in data.items():
                setattr(existing, k, v)
        else:
            profile = Profile(user_id=user.id, **data)
            session.add(profile)
            
        user.status = "active"
        await session.commit()
        
        await state.clear()
        from keyboards.main import get_main_menu_kb
        await message.answer(t_prof["profile_saved"], reply_markup=get_main_menu_kb())
        return
        
    await message.answer("Tugmalardan birini tanlang.", reply_markup=get_confirm_kb())
