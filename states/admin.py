# states/admin.py
from aiogram.fsm.state import StatesGroup, State

class AdminAddService(StatesGroup):
    name = State()
    address = State()
    phone = State()
    hours = State()
    days_off = State()
    category = State()
    location = State()
    image = State()
    confirm = State()

class AdminEditService(StatesGroup):
    choosing_service = State()
    edit_menu = State()
    edit_name = State()
    edit_address = State()
    edit_phone = State()
    edit_hours = State()
    edit_days_off = State()
    edit_category = State()
    edit_location = State()
    edit_image = State()

class AdminAddWash(StatesGroup):
    name = State()
    address = State()
    phone = State()
    hours = State()
    location = State()
    image = State()
    confirm = State()


# states/admin.py (oxiriga qo'shing)
class AdminPartnerReview(StatesGroup):
    choosing = State()
    viewing = State()
