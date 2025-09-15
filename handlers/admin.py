from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from keyboards.admin_reply import admin_panel_kb, ask_location_kb
from keyboards.admin_inline import categories_kb, services_list_kb, edit_menu_kb, CATEGORIES
from keyboards.reply import main_menu
from states.admin import AdminAddService, AdminEditService, AdminAddWash
from database import (
    is_admin, get_user_language, SessionLocal, ServicePoint,
    admin_create_or_migrate, create_service_point, update_service_point,
    fetch_services_page, delete_service_point, toggle_service_today_closed
)

router = Router()

# --------- Guard -----------
async def ensure_admin(event_user_id: int) -> bool:
    return await is_admin(event_user_id)

# --------- /admin ----------
@router.message(Command("admin"))
async def enter_admin(message: types.Message, state: FSMContext):
    if not await ensure_admin(message.from_user.id):
        await message.answer("⛔️ Admin only")
        return
    lang = await get_user_language(message.from_user.id)
    await admin_create_or_migrate()
    await state.update_data(trail=["admin_root"])
    await message.answer(
        "🛠 Admin panelga xush kelibsiz!" if lang != "ru" else "🛠 Добро пожаловать в админ-панель!",
        reply_markup=admin_panel_kb(lang)
    )

# --------- Add Service flow ----------
@router.message(F.text.in_(["➕ Avtoservis qo‘shish", "➕ Добавить автосервис"]))
async def add_service_start(message: types.Message, state: FSMContext):
    if not await ensure_admin(message.from_user.id):
        return
    lang = await get_user_language(message.from_user.id)
    await state.set_state(AdminAddService.name)
    await message.answer("🏷 Avtoservis nomini kiriting:" if lang != "ru" else "🏷 Введите название автосервиса:")

@router.message(AdminAddService.name, F.text)
async def add_service_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    lang = await get_user_language(message.from_user.id)
    await state.set_state(AdminAddService.address)
    await message.answer("🏠 Manzilni kiriting:" if lang != "ru" else "🏠 Введите адрес:")

@router.message(AdminAddService.address, F.text)
async def add_service_addr(message: types.Message, state: FSMContext):
    await state.update_data(address=message.text.strip())
    lang = await get_user_language(message.from_user.id)
    await state.set_state(AdminAddService.phone)
    await message.answer("📞 Telefon raqamni kiriting (+998...):" if lang != "ru" else "📞 Введите телефон (+998...):")

@router.message(AdminAddService.phone, F.text)
async def add_service_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text.strip())
    lang = await get_user_language(message.from_user.id)
    await state.set_state(AdminAddService.hours)
    await message.answer("🕒 Ish vaqti (09:00-18:00):" if lang != "ru" else "🕒 Время работы (09:00-18:00):")

@router.message(AdminAddService.hours, F.text)
async def add_service_hours(message: types.Message, state: FSMContext):
    await state.update_data(hours=message.text.strip())
    lang = await get_user_language(message.from_user.id)
    await state.set_state(AdminAddService.days_off)
    await message.answer("📅 Dam kunlari (masalan: Yakshanba yoki '-'):" if lang != "ru" else "📅 Выходные (например: Воскресенье или '-'):")

@router.message(AdminAddService.days_off, F.text)
async def add_service_days_off(message: types.Message, state: FSMContext):
    await state.update_data(days_off=message.text.strip())
    lang = await get_user_language(message.from_user.id)
    await state.set_state(AdminAddService.category)
    await state.update_data(categories=set())
    await message.answer("🏷 Kategoriya(lar)ni tanlang:" if lang != "ru" else "🏷 Выберите категории:",
                         reply_markup=categories_kb(set(), lang))

@router.callback_query(AdminAddService.category, F.data.startswith("cat:"))
async def add_service_select_cat(cb: types.CallbackQuery, state: FSMContext):
    lang = await get_user_language(cb.from_user.id)
    key = cb.data.split(":")[1]
    data = await state.get_data()
    selected: set = set(data.get("categories", set()))

    if key == "save":
        await state.set_state(AdminAddService.location)
        await cb.message.edit_text("📍 Lokatsiyani yuboring:" if lang != "ru" else "📍 Отправьте геолокацию:", reply_markup=None)
        await cb.message.answer("📍", reply_markup=ask_location_kb(lang))
        await cb.answer()
        return

    if key == "cancel":
        await state.set_state(AdminAddService.category)
        await cb.message.edit_text("Bekor qilindi." if lang != "ru" else "Отменено.", reply_markup=None)
        await cb.answer()
        return

    all_keys = [k for _, k in CATEGORIES]
    if key in all_keys:
        if key in selected:
            selected.remove(key)
        else:
            selected.add(key)
        await state.update_data(categories=selected)
        await cb.message.edit_reply_markup(reply_markup=categories_kb(selected, lang))  # ✅ fixed
    await cb.answer()

@router.message(AdminAddService.location, F.location)
async def add_service_location(message: types.Message, state: FSMContext):
    await state.update_data(lat=message.location.latitude, lon=message.location.longitude)
    lang = await get_user_language(message.from_user.id)
    await state.set_state(AdminAddService.image)
    await message.answer("🖼 Rasm URL yuboring (yoki 'skip'):" if lang != "ru" else "🖼 Отправьте URL изображения (или 'skip'):")

@router.message(AdminAddService.image, F.text)
async def add_service_image(message: types.Message, state: FSMContext):
    img = message.text.strip()
    if img.lower() == "skip":
        img = "https://placehold.co/600x400?text=Avtoservis"
    await state.update_data(image_url=img)
    data = await state.get_data()
    lang = await get_user_language(message.from_user.id)
    cats = ", ".join([lbl for lbl, key in CATEGORIES if key in data.get("categories", set())]) or "-"
    preview = (
        f"✅ Tasdiqlaysizmi?\n"
        f"Nom: {data.get('name')}\n"
        f"Manzil: {data.get('address')}\n"
        f"Telefon: {data.get('phone')}\n"
        f"Ish vaqti: {data.get('hours')}\n"
        f"Dam kunlari: {data.get('days_off')}\n"
        f"Kategoriya: {cats}\n"
        f"Lat/Lon: {data.get('lat')}, {data.get('lon')}\n"
        f"Rasm: {img}\n"
    ) if lang != "ru" else (
        f"✅ Подтвердить?\n"
        f"Название: {data.get('name')}\n"
        f"Адрес: {data.get('address')}\n"
        f"Телефон: {data.get('phone')}\n"
        f"Время: {data.get('hours')}\n"
        f"Выходные: {data.get('days_off')}\n"
        f"Категории: {cats}\n"
        f"Lat/Lon: {data.get('lat')}, {data.get('lon')}\n"
        f"Фото: {img}\n"
    )
    await state.set_state(AdminAddService.confirm)
    await message.answer(preview + ("\nYuborish uchun 'ha', bekor uchun 'yo‘q'." if lang != "ru" else "\nДля сохранения — 'да', отмена — 'нет'."))

@router.message(AdminAddService.confirm, F.text.lower().in_(["ha","да","yo‘q","нет"]))
async def add_service_confirm(message: types.Message, state: FSMContext):
    ok = message.text.lower() in ["ha", "да"]
    lang = await get_user_language(message.from_user.id)
    if not ok:
        await state.clear()
        await message.answer("Bekor qilindi." if lang != "ru" else "Отменено.", reply_markup=admin_panel_kb(lang))
        return
    data = await state.get_data()
    async with SessionLocal() as session:
        await create_service_point(
            session=session,
            name=data["name"],
            address=data["address"],
            phone=data["phone"],
            hours=data["hours"],
            days_off=data["days_off"],
            categories=list(data.get("categories", [])),
            lat=data["lat"],
            lon=data["lon"],
            image_url=data["image_url"],
            category="service"
        )
    await state.clear()
    await message.answer("✅ Saqlandi!" if lang != "ru" else "✅ Сохранено!", reply_markup=admin_panel_kb(lang))

# --------- Services list & edit ----------
PAGE_SIZE = 10

@router.message(F.text.in_(["📋 Avtoservislar ro‘yxati", "📋 Список автосервисов"]))
async def list_services(message: types.Message, state: FSMContext):
    if not await ensure_admin(message.from_user.id):
        return
    lang = await get_user_language(message.from_user.id)
    page = 1
    items, has_next = await fetch_services_page(page=page, page_size=PAGE_SIZE, category="service")
    if not items:
        await message.answer("Hali ma'lumot yo‘q." if lang != "ru" else "Пока нет данных.")
        return
    await state.set_state(AdminEditService.choosing_service)
    await message.answer("Quyidagidan tanlang:" if lang != "ru" else "Выберите из списка:",
                         reply_markup=services_list_kb(items, page, has_next))

@router.callback_query(AdminEditService.choosing_service, F.data.startswith("pg:"))
async def paginate_services(cb: types.CallbackQuery, state: FSMContext):
    page = int(cb.data.split(":")[1])
    items, has_next = await fetch_services_page(page=page, page_size=PAGE_SIZE, category="service")
    await cb.message.edit_reply_markup(reply_markup=services_list_kb(items, page, has_next))  # ✅ fixed
    await cb.answer()

@router.callback_query(AdminEditService.choosing_service, F.data.startswith("svc:"))
async def choose_service_to_edit(cb: types.CallbackQuery, state: FSMContext):
    sid = int(cb.data.split(":")[1])
    lang = await get_user_language(cb.from_user.id)
    await state.update_data(edit_sid=sid)
    await state.set_state(AdminEditService.edit_menu)
    await cb.message.edit_text("Tahrirlash menyusi:" if lang != "ru" else "Меню редактирования:")
    await cb.message.edit_reply_markup(reply_markup=edit_menu_kb(lang, sid))  # ✅ fixed
    await cb.answer()

# --- Edit categories (multi-select)
@router.callback_query(AdminEditService.edit_menu, F.data.startswith("editcat:"))
async def ask_edit_cat(cb: types.CallbackQuery, state: FSMContext):
    sid = int(cb.data.split(":")[1])
    lang = await get_user_language(cb.from_user.id)
    async with SessionLocal() as session:
        sp = await session.get(ServicePoint, sid)
        selected = set((sp.sub_categories or "").split(",")) if sp and sp.sub_categories else set()
    await state.set_state(AdminEditService.edit_category)
    await state.update_data(edit_sid=sid, edit_cat_selected=selected)
    await cb.message.answer("🏷 Kategoriya(lar)ni tanlang:" if lang != "ru" else "🏷 Выберите категории:")
    await cb.message.edit_reply_markup(reply_markup=categories_kb(selected, lang))  # ✅ fixed
    await cb.answer()

@router.callback_query(AdminEditService.edit_category, F.data.startswith("cat:"))
async def edit_categories_select(cb: types.CallbackQuery, state: FSMContext):
    lang = await get_user_language(cb.from_user.id)
    key = cb.data.split(":")[1]
    data = await state.get_data()
    selected: set = set(data.get("edit_cat_selected", set()))
    sid = data["edit_sid"]

    if key == "save":
        async with SessionLocal() as session:
            await update_service_point(session, sid, {"sub_categories": ",".join([k for k in selected if k])})
        await cb.message.answer("✅ Saqlandi." if lang != "ru" else "✅ Сохранено.")
        await state.set_state(AdminEditService.edit_menu)
        await cb.answer()
        return

    if key == "cancel":
        await state.set_state(AdminEditService.edit_menu)
        await cb.message.answer("Bekor qilindi." if lang != "ru" else "Отменено.")
        await cb.answer()
        return

    all_keys = [k for _, k in CATEGORIES]
    if key in all_keys:
        if key in selected:
            selected.remove(key)
        else:
            selected.add(key)
        await state.update_data(edit_cat_selected=selected)
        await cb.message.edit_reply_markup(reply_markup=categories_kb(selected, lang))  # ✅ fixed
    await cb.answer()
