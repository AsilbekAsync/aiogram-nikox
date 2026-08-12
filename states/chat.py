from aiogram.fsm.state import State, StatesGroup

class ChatForm(StatesGroup):
    active_chat = State()
