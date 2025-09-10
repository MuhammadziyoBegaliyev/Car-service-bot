from aiogram.fsm.state import StatesGroup, State

class Register(StatesGroup):
    full_name = State()
    contact = State()
