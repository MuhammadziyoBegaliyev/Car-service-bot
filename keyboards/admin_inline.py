# keyboards/admin_inline.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

CATEGORIES = [
    ("⚡️ Elektrchi","electric"),
    ("🛠 Kuzov ta’miri","body"),
    ("🔩 Motorchi","motor"),
    ("🛞 Vulkanizatsiya","vulcan"),
    ("🎯 G‘ildirak tekislash","align"),
    ("🕶 Tonirovka","tint"),
    ("🔇 Shovqin izolyatsiyasi","noise"),
    ("🧰 Universal","universal"),
]

def categories_kb(selected: set[str] | None = None, lang: str = "uz"):
    selected = selected or set()
    rows = []
    for label, key in CATEGORIES:
        mark = "✅" if key in selected else "☑️"
        rows.append([InlineKeyboardButton(text=f"{mark} {label}", callback_data=f"cat:{key}")])
    rows.append([
        InlineKeyboardButton(text=("Сохранить" if lang=="ru" else "Saqlash"), callback_data="cat:save"),
        InlineKeyboardButton(text=("Отмена" if lang=="ru" else "Bekor qilish"), callback_data="cat:cancel"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def services_list_kb(items: list[tuple[int,str]], page: int = 1, has_next: bool = False):
    """
    items: list of (service_id, title)
    """
    rows = []
    for sid, title in items:
        rows.append([InlineKeyboardButton(text=title, callback_data=f"svc:{sid}")])
    nav = []
    if page > 1:
        nav.append(InlineKeyboardButton(text="⬅️", callback_data=f"pg:{page-1}"))
    if has_next:
        nav.append(InlineKeyboardButton(text="➡️", callback_data=f"pg:{page+1}"))
    if nav:
        rows.append(nav)
    return InlineKeyboardMarkup(inline_keyboard=rows)

def edit_menu_kb(lang: str, sid: int):
    tx = (lambda uz,ru: ru if lang=="ru" else uz)
    rows = [
        [InlineKeyboardButton(text=tx("✏️ Nom", "✏️ Название"), callback_data=f"editname:{sid}"),
         InlineKeyboardButton(text=tx("🏠 Manzil", "🏠 Адрес"), callback_data=f"editaddr:{sid}")],
        [InlineKeyboardButton(text=tx("📞 Telefon", "📞 Телефон"), callback_data=f"editphone:{sid}"),
         InlineKeyboardButton(text=tx("🕒 Ish vaqti", "🕒 Время работы"), callback_data=f"edithours:{sid}")],
        [InlineKeyboardButton(text=tx("📅 Dam kunlari", "📅 Выходные"), callback_data=f"editdays:{sid}"),
         InlineKeyboardButton(text=tx("🧭 Lokatsiya", "🧭 Локация"), callback_data=f"editloc:{sid}")],
        [InlineKeyboardButton(text=tx("🏷 Kategoriya", "🏷 Категория"), callback_data=f"editcat:{sid}"),
         InlineKeyboardButton(text=tx("🖼 Rasm", "🖼 Фото"), callback_data=f"editimg:{sid}")],
        [InlineKeyboardButton(text=tx("⛔️ Bugun yopiq/ochiq", "⛔️ Сегодня закрыт/открыт"), callback_data=f"toggle:{sid}")],
        [InlineKeyboardButton(text=tx("🗑 O‘chirish", "🗑 Удалить"), callback_data=f"delete:{sid}")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)





# keyboards/admin_inline.py (oxiriga qo'shing)
def partners_list_kb(items: list[tuple[int, str]], page: int = 1, has_next: bool = False):
    rows = []
    for pid, title in items:
        rows.append([InlineKeyboardButton(text=title, callback_data=f"prv:{pid}")])
    nav = []
    if page > 1:
        nav.append(InlineKeyboardButton(text="⬅️", callback_data=f"ppg:{page-1}"))
    if has_next:
        nav.append(InlineKeyboardButton(text="➡️", callback_data=f"ppg:{page+1}"))
    if nav:
        rows.append(nav)
    return InlineKeyboardMarkup(inline_keyboard=rows)

def partner_decision_kb(pid: int, lang: str):
    yes = "✅ Tasdiqlash" if lang != "ru" else "✅ Одобрить"
    no  = "🚫 Rad etish"  if lang != "ru" else "🚫 Отклонить"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=yes, callback_data=f"pdec:ok:{pid}"),
         InlineKeyboardButton(text=no,  callback_data=f"pdec:no:{pid}")]
    ])
