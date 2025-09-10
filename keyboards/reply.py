from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def back_text(lang: str) -> str:
    return "◀️ Назад" if lang == "ru" else "◀️ Orqaga"

def main_menu(lang: str):
    """
    Asosiy menyu + doimiy 'Orqaga' tugmasi.
    """
    if lang == "ru":
        buttons = [
            [KeyboardButton(text="🔧 Автосервисы")],
            [KeyboardButton(text="🧽 Мойка")],
            [KeyboardButton(text="🛡️ Противоугонная система")],
            [KeyboardButton(text="⛽️ Доставка топлива")],
            [KeyboardButton(text="🤝 Сотрудничество")],
            [KeyboardButton(text=back_text(lang))],  # Doimiy Orqaga
        ]
    else:
        buttons = [
            [KeyboardButton(text="🔧 Avtoservislar")],
            [KeyboardButton(text="🧽 Moyka")],
            [KeyboardButton(text="🛡️ Bloklashga qarshi tizim")],
            [KeyboardButton(text="⛽️ Yoqilg‘i yetkazib berish")],
            [KeyboardButton(text="🤝 Hamkorlik")],
            [KeyboardButton(text=back_text(lang))],  # Doimiy Orqaga
        ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def request_contact_kb(lang: str):
    """
    Ro‘yxatdan o‘tishda kontakt so‘rash + Orqaga
    """
    text = "📲 Поделиться контактом" if lang == "ru" else "📲 Kontaktni ulashish"
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=text, request_contact=True)],
            [KeyboardButton(text=back_text(lang))],  # Orqaga
        ],
        resize_keyboard=True
    )

def request_location_kb(lang: str):
    """
    Geo so‘rash bosqichi + Orqaga
    """
    text = "📍 Отправить геолокацию" if lang == "ru" else "📍 Lokatsiya yuborish"
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=text, request_location=True)],
            [KeyboardButton(text=back_text(lang))],  # Orqaga
        ],
        resize_keyboard=True
    )
