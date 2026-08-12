from aiogram.fsm.state import State, StatesGroup

class SearchForm(StatesGroup):
    gender = State()
    age_min = State()
    age_max = State()
    viewing = State()
