from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from keyboards.inline import service_filters, call_loc_kb, request_actions_kb
from keyboards.reply import request_location_kb, back_only_kb  # ⬅️ main_menu o‘rniga back_only_kb import
from database import get_user_language, find_nearest, SessionLocal, ServicePoint
from utils.i18n import t
from config import settings

router = Router()

async def trail_push(state: FSMContext, key: str):
    data = await state.get_data()
    trail = data.get("trail", ["root"])
    trail.append(key)
    await state.update_data(trail=trail)

@router.callback_query(F.data.startswith("filter:"))
async def filter_selected(cb: types.CallbackQuery, state: FSMContext):
    lang = await get_user_language(cb.from_user.id)
    sub = cb.data.split(":")[1]
    await state.update_data(chosen_sub=sub, flag_cat="service")
    await trail_push(state, "service_geo")
    await cb.message.answer(t("ask_geo", lang), reply_markup=request_location_kb(lang))
    await cb.answer()

@router.callback_query(F.data == "back:menu")
async def back_menu(cb: types.CallbackQuery):
    lang = await get_user_language(cb.from_user.id)
    # Asosiy menyuga qaytarishni back handler qiladi; bu yerda faqat matn yuborish mumkin.
    await cb.message.answer(t("menu_title", lang))
    await cb.answer()

@router.callback_query(F.data == "back:services")
async def back_services(cb: types.CallbackQuery):
    lang = await get_user_language(cb.from_user.id)
    await cb.message.answer(t("services_choose", lang), reply_markup=service_filters(lang))
    await cb.answer()

# Faqat State=None bo‘lsa (oddiy foydalanuvchi oqimi) “eng yaqin” ishlaydi
@router.message(StateFilter(None), F.location)
async def handle_location(message: types.Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    data = await state.get_data()
    sub = data.get("chosen_sub")
    category = data.get("flag_cat") or ("service" if sub else "wash")

    lat = message.location.latitude
    lon = message.location.longitude

    points = await find_nearest(category, lat, lon, sub_type=sub if category == "service" else None)

    if not points:
        await message.answer(t("nearest_none", lang), reply_markup=back_only_kb(lang))  # ⬅️ faqat orqaga
        await trail_push(state, "results")
        return

    await message.answer(t("nearest_found", lang))

    for dist, sp in points:
        caption = (
            f"{t('card_name', lang)}: {sp.name}\n"
            f"{t('card_addr', lang)}: {sp.address}\n"
            f"{t('card_phone', lang)}: {sp.phone}\n"
            f"{t('card_hours', lang)}: {sp.hours}\n"
            f"📏 {dist:.1f} km"
        )
        try:
            await message.bot.send_photo(
                chat_id=message.chat.id,
                photo=sp.image_url,
                caption=caption,
                reply_markup=call_loc_kb(sp.phone, sp.id, lang)
            )
        except Exception:
            await message.answer(caption, reply_markup=call_loc_kb(sp.phone, sp.id, lang))

    # Natija ostida: inline so‘rov tugmalari + reply’da faqat “Orqaga”
    await message.answer(t("request_options", lang), reply_markup=request_actions_kb(lang))
    await message.answer(t("back_hint", lang), reply_markup=back_only_kb(lang))  # ⬅️ endi menyuga sakramaydi
    await trail_push(state, "results")

@router.callback_query(F.data.startswith("fueltype:"))
async def choose_fueltype(cb: types.CallbackQuery, state: FSMContext):
    lang = await get_user_language(cb.from_user.id)
    code = cb.data.split(":")[1]
    await state.update_data(flag_cat="fuel", fuel_type=code, chosen_sub=None)
    await trail_push(state, "fuel_geo")
    await cb.message.answer(t("ask_geo", lang), reply_markup=request_location_kb(lang))
    await cb.answer()

@router.callback_query(F.data.startswith("loc:"))
async def send_sp_location(cb: types.CallbackQuery):
    sp_id = int(cb.data.split(":")[1])
    async with SessionLocal() as session:
        sp = await session.get(ServicePoint, sp_id)
        if not sp:
            await cb.answer("Not found", show_alert=True)
            return
        await cb.message.bot.send_location(chat_id=cb.message.chat.id, latitude=sp.lat, longitude=sp.lon)
        await cb.answer()

@router.callback_query(F.data.startswith("call:"))
async def send_sp_contact(cb: types.CallbackQuery):
    sp_id = int(cb.data.split(":")[1])
    async with SessionLocal() as session:
        sp = await session.get(ServicePoint, sp_id)
        if not sp:
            await cb.answer("Not found", show_alert=True)
            return
        raw = (sp.phone or "").strip()
        digits = "".join(ch for ch in raw if ch.isdigit() or ch == "+")
        if not digits:
            await cb.message.answer("☎️ Telefon raqami mavjud emas.")
            await cb.answer(); return
        if not digits.startswith("+"):
            digits = "+" + digits if not digits.startswith("998") else "+" + digits
        try:
            await cb.message.bot.send_contact(chat_id=cb.message.chat.id, phone_number=digits, first_name=sp.name[:64] if sp.name else "Service")
        except Exception:
            await cb.message.answer(f"☎️ {sp.name}\n{digits}")
        await cb.answer()

@router.callback_query(F.data.startswith("req:"))
async def send_request(cb: types.CallbackQuery):
    code = cb.data.split(":")[1]
    lang = await get_user_language(cb.from_user.id)
    text = {"anti":"🛡️","tow":"🚚","fuel":"⛽️"}.get(code,"") + f" Request from user {cb.from_user.id}"
    for admin in settings.admin_ids:
        try:
            await cb.message.bot.send_message(admin, f"📩 {text}")
        except Exception:
            pass
    await cb.message.answer(t("request_sent", lang))
    await cb.answer()
