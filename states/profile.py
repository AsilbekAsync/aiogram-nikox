from aiogram.fsm.state import State, StatesGroup

class ProfileForm(StatesGroup):
    gender = State()
    age = State()
    height = State()
    weight = State()
    nationality = State()
    marital_status = State()
    location = State()
    original_location = State()
    religion = State()
    languages_count = State()
    bio = State()
    partner_requirements = State()
    filled_by = State()
    
    # Female specifics
    children_count = State()
    hijab = State()
    relocation = State()
    second_wife = State()
    
    preview = State()
