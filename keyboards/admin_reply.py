# keyboards/admin_reply.py
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def back_text(lang: str) -> str:
    return "◀️ Назад" if lang == "ru" else "◀️ Orqaga"

def admin_panel_kb(lang: str):
    if lang == "ru":
        rows = [
            [KeyboardButton(text="➕ Добавить автосервис")],
            [KeyboardButton(text="📋 Список автосервисов")],
            [KeyboardButton(text="🧽 Добавить мойку")],
            [KeyboardButton(text=back_text(lang))]
        ]
    else:
        rows = [
            [KeyboardButton(text="➕ Avtoservis qo‘shish")],
            [KeyboardButton(text="📋 Avtoservislar ro‘yxati")],
            [KeyboardButton(text="🧽 Moyka qo‘shish")],
            [KeyboardButton(text=back_text(lang))]
        ]
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)



    # keyboards/admin_reply.py (admin_panel_kb ichida tugmalar ro'yxatiga qo'shing)
def admin_panel_kb(lang: str):
    if lang == "ru":
        rows = [
            [KeyboardButton(text="➕ Добавить автосервис")],
            [KeyboardButton(text="📋 Список автосервисов")],
            [KeyboardButton(text="🧽 Добавить мойку")],
            [KeyboardButton(text="🤝 Заявки сотрудничества")],   # ⬅️ Yangi
            [KeyboardButton(text=back_text(lang))]
        ]
    else:
        rows = [
            [KeyboardButton(text="➕ Avtoservis qo‘shish")],
            [KeyboardButton(text="📋 Avtoservislar ro‘yxati")],
            [KeyboardButton(text="🧽 Moyka qo‘shish")],
            [KeyboardButton(text="🤝 Hamkorlik so‘rovlari")],    # ⬅️ Yangi
            [KeyboardButton(text=back_text(lang))]
        ]
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)




def ask_location_kb(lang: str):
    text = "📍 Отправить геолокацию" if lang == "ru" else "📍 Lokatsiya yuborish"
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=text, request_location=True)],
            [KeyboardButton(text=back_text(lang))]
        ],
        resize_keyboard=True
    )
