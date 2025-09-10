from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from states import PartnerStates
from keyboards.reply import request_location_kb, main_menu
from keyboards.inline import admin_approve_kb
from database import get_user_language
from utils.i18n import t
from config import settings

router = Router()

@router.message(F.text.in_(["🤝 Hamkorlik","🤝 Сотрудничество"]))
async def partner_start(message: types.Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    await message.answer(t("partner_company", lang))
    await state.set_state(PartnerStates.company)

@router.message(PartnerStates.company)
async def partner_phone(message: types.Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    await state.update_data(company=message.text.strip())
    await message.answer(t("partner_phone", lang))
    await state.set_state(PartnerStates.phone)

@router.message(PartnerStates.phone)
async def partner_services(message: types.Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    await state.update_data(phone=message.text.strip())
    await message.answer(t("partner_services", lang))
    await state.set_state(PartnerStates.services)

@router.message(PartnerStates.services)
async def partner_geo(message: types.Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    await state.update_data(services=message.text.strip())
    await message.answer(t("partner_geo", lang), reply_markup=request_location_kb(lang))
    await state.set_state(PartnerStates.geo)

@router.message(PartnerStates.geo, F.location)
async def partner_hours(message: types.Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    await state.update_data(lat=message.location.latitude, lon=message.location.longitude)
    await message.answer(t("partner_hours", lang))
    await state.set_state(PartnerStates.hours)

@router.message(PartnerStates.hours)
async def partner_finish(message: types.Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    await state.update_data(hours=message.text.strip())
    data = await state.get_data()

    summary = (f"{t('admin_new_partner',lang)}\n"
               f"👤 UserID: {message.from_user.id}\n"
               f"🏢 {data.get('company')}\n"
               f"☎️ {data.get('phone')}\n"
               f"🔧 {data.get('services')}\n"
               f"📍 {data.get('lat')}, {data.get('lon')}\n"
               f"⏰ {data.get('hours')}")
    for admin in settings.admin_ids:
        try:
            await message.bot.send_message(admin, summary, reply_markup=admin_approve_kb(message.from_user.id, lang))
        except Exception:
            pass

    await message.answer(t("partner_done", lang), reply_markup=main_menu(lang))
    await state.clear()

@router.callback_query(F.data.startswith("approve:"))
async def approve_partner(cb: types.CallbackQuery):
    uid = int(cb.data.split(":")[1])
    lang = await get_user_language(uid)
    try:
        await cb.message.bot.send_message(uid, t("approved_msg", lang))
    except Exception:
        pass
    await cb.answer("Approved")

@router.callback_query(F.data.startswith("reject:"))
async def reject_partner(cb: types.CallbackQuery):
    uid = int(cb.data.split(":")[1])
    lang = await get_user_language(uid)
    try:
        await cb.message.bot.send_message(uid, t("rejected_msg", lang))
    except Exception:
        pass
    await cb.answer("Rejected")
