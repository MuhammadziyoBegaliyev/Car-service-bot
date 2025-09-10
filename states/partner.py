from aiogram.fsm.state import StatesGroup, State

class PartnerStates(StatesGroup):
    company = State()
    phone = State()
    services = State()
    geo = State()
    hours = State()
