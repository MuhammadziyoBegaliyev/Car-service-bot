from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from database import get_user_language
from keyboards.inline import service_filters, fuel_types_kb
from keyboards.reply import request_location_kb, main_menu, back_text
from utils.i18n import t

router = Router()

# ---------- Breadcrumb helpers ----------
async def trail_get(state: FSMContext) -> list[str]:
    data = await state.get_data()
    return data.get("trail", ["root"])

async def trail_set(state: FSMContext, trail: list[str]):
    await state.update_data(trail=trail)

async def trail_push(state: FSMContext, key: str):
    trail = await trail_get(state)
    trail.append(key)
    await trail_set(state, trail)

async def trail_pop(state: FSMContext) -> str:
    trail = await trail_get(state)
    if len(trail) > 1:
        trail.pop()
    await trail_set(state, trail)
    return trail[-1]

# ---------- Main menu entries ----------
@router.message(F.text.in_(["🔧 Avtoservislar", "🔧 Автосервисы"]))
async def enter_services(message: types.Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    await trail_push(state, "services")
    # Inline filtrni ko‘rsatamiz (reply klaviatura oxirgi holatda qoladi — odatda main_menu)
    await message.answer(t("services_choose", lang), reply_markup=service_filters(lang))

@router.message(F.text.in_(["🧽 Moyka", "🧽 Мойка"]))
async def enter_wash(message: types.Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    # services.py lokatsiya handleri category=wash bo‘lishi uchun flagni o‘rnatamiz:
    await state.update_data(flag_cat="wash", chosen_sub=None)
    await trail_push(state, "wash_geo")
    await message.answer(t("ask_geo", lang), reply_markup=request_location_kb(lang))

@router.message(F.text.in_(["🛡️ Bloklashga qarshi tizim", "🛡️ Противоугонная система"]))
async def enter_anti(message: types.Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    await state.update_data(flag_cat="anti_theft", chosen_sub=None)
    await trail_push(state, "anti_geo")
    await message.answer(t("ask_geo", lang), reply_markup=request_location_kb(lang))

@router.message(F.text.in_(["⛽️ Yoqilg‘i yetkazib berish", "⛽️ Доставка топлива"]))
async def enter_fuel(message: types.Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    await trail_push(state, "fuel_type")
    await message.answer(t("fuel_ask_type", lang), reply_markup=fuel_types_kb(lang))

# ---------- Global "Orqaga" reply tugmasi ----------
@router.message(F.text.func(lambda x: x in ["◀️ Orqaga", "◀️ Назад"]))
async def go_back(message: types.Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    current = await trail_pop(state)  # bir qadam ortga

    # Qaysi ekranga qaytamiz?
    if current == "root":
        # Asosiy menyu
        await message.answer(t("menu_title", lang), reply_markup=main_menu(lang))

    elif current == "services":
        # Avtoservislar filtr ekrani
        await message.answer(t("services_choose", lang), reply_markup=service_filters(lang))

    elif current in ("wash_geo", "anti_geo", "fuel_geo", "service_geo"):
        # Geolokatsiya so‘rash ekrani
        await message.answer(t("ask_geo", lang), reply_markup=request_location_kb(lang))

    elif current == "fuel_type":
        # Yoqilg‘i turi tanlashga qaytish
        await message.answer(t("fuel_ask_type", lang), reply_markup=fuel_types_kb(lang))

    elif current == "results":
        # Natija sahifasidan orqaga — odatda asosiy menyu
        await message.answer(t("menu_title", lang), reply_markup=main_menu(lang))

    else:
        # Noma’lum bo‘lsa, rootga
        await trail_set(state, ["root"])
        await message.answer(t("menu_title", lang), reply_markup=main_menu(lang))
