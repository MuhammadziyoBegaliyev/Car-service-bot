from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def lang_choice():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇺🇿 O‘zbekcha", callback_data="lang:uz"),
         InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru")]
    ])

def service_filters(lang: str):
    items_uz = [
        ("⚡️ Elektrchi","electric"),
        ("🛠️ Kuzov ta’miri","body"),
        ("🔩 Motorchi","motor"),
        ("🛞 Vulkanizatsiya","vulcan"),
        ("🎯 G‘ildirak tekislash","align"),
        ("🕶️ Tonirovka","tint"),
        ("🔇 Shovqin izolyatsiyasi","noise"),
        ("🧰 Universal","universal"),
    ]
    items_ru = [
        ("⚡️ Электрик","electric"),
        ("🛠️ Кузовной ремонт","body"),
        ("🔩 Моторист","motor"),
        ("🛞 Вулканизация","vulcan"),
        ("🎯 Развал-схождение","align"),
        ("🕶️ Тонировка","tint"),
        ("🔇 Шумоизоляция","noise"),
        ("🧰 Универсал","universal"),
    ]
    items = items_ru if lang=="ru" else items_uz
    rows = [[InlineKeyboardButton(text=txt, callback_data=f"filter:{key}")] for txt,key in items]
    rows.append([InlineKeyboardButton(text="◀️ Orqaga" if lang!="ru" else "◀️ Назад", callback_data="back:menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def call_loc_kb(phone: str, sp_id: int, lang: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="📞 Qo‘ng‘iroq qilish" if lang != "ru" else "📞 Позвонить",
            callback_data=f"call:{sp_id}"  # URL O‘RNIGA CALLBACK!
        ),
         InlineKeyboardButton(
            text="🗺️ Lokatsiya" if lang != "ru" else "🗺️ Локация",
            callback_data=f"loc:{sp_id}"
        )],
        [InlineKeyboardButton(
            text="◀️ Orqaga" if lang != "ru" else "◀️ Назад",
            callback_data="back:services"
        )]
    ])


def request_actions_kb(lang: str):
    rows = [[InlineKeyboardButton(text=("🛡️ Bloklashga qarshi tizim" if lang!="ru" else "🛡️ Противоугонная система"), callback_data="req:anti")],
            [InlineKeyboardButton(text=("🚚 Evakuator" if lang!="ru" else "🚚 Эвакуатор"), callback_data="req:tow")],
            [InlineKeyboardButton(text=("⛽️ Yoqilg‘i yetkazib berish" if lang!="ru" else "⛽️ Доставка топлива"), callback_data="req:fuel")]]
    return InlineKeyboardMarkup(inline_keyboard=rows)

def fuel_types_kb(lang: str):
    labels = [("AI-80","ai80"),("AI-92","ai92"),("AI-95","ai95"),("Dizel","dizel")] if lang!="ru" else [("АИ-80","ai80"),("АИ-92","ai92"),("АИ-95","ai95"),("Дизель","dizel")]
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t, callback_data=f"fueltype:{k}")] for t,k in labels])

def admin_approve_kb(uid: int, lang: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=("✅ Qabul qilish" if lang!="ru" else "✅ Принять"), callback_data=f"approve:{uid}"),
         InlineKeyboardButton(text=("❌ Rad etish" if lang!="ru" else "❌ Отклонить"), callback_data=f"reject:{uid}")]
    ])
