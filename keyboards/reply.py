from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def back_text(lang: str) -> str:
    return "◀️ Назад" if lang == "ru" else "◀️ Orqaga"

def main_menu(lang: str) -> ReplyKeyboardMarkup:
    if lang == "ru":
        buttons = [
            [KeyboardButton(text="🔧 Автосервисы")],
            [KeyboardButton(text="🧽 Мойка")],
            [KeyboardButton(text="🛡️ Противоугонная система")],
            [KeyboardButton(text="⛽️ Доставка топлива")],
            [KeyboardButton(text="🤝 Сотрудничество")],
            [KeyboardButton(text=back_text(lang))],  # doimiy orqaga
        ]
    else:
        buttons = [
            [KeyboardButton(text="🔧 Avtoservislar")],
            [KeyboardButton(text="🧽 Moyka")],
            [KeyboardButton(text="🛡️ Bloklashga qarshi tizim")],
            [KeyboardButton(text="⛽️ Yoqilg‘i yetkazib berish")],
            [KeyboardButton(text="🤝 Hamkorlik")],
            [KeyboardButton(text=back_text(lang))],  # doimiy orqaga
        ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def request_contact_kb(lang: str) -> ReplyKeyboardMarkup:
    text = "📲 Поделиться контактом" if lang == "ru" else "📲 Kontaktni ulashish"
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=text, request_contact=True)],
            [KeyboardButton(text=back_text(lang))],
        ],
        resize_keyboard=True
    )

def request_location_kb(lang: str) -> ReplyKeyboardMarkup:
    text = "📍 Отправить геолокацию" if lang == "ru" else "📍 Lokatsiya yuborish"
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=text, request_location=True)],
            [KeyboardButton(text=back_text(lang))],
        ],
        resize_keyboard=True
    )

# ⬇️ Yangi: faqat “Orqaga” bo‘lgan klaviatura
def back_only_kb(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=back_text(lang))]],
        resize_keyboard=True
    )
