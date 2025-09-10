from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from keyboards.inline import lang_choice
from keyboards.reply import request_contact_kb, main_menu
from states import Register
from database import upsert_user
from utils.i18n import t
from config import settings

router = Router()

@router.message(CommandStart())
async def start_cmd(message: types.Message, state: FSMContext):
    # Trail reset: har doim ildiz holatiga qaytaramiz
    await state.clear()
    await state.update_data(trail=["root"])
    await message.answer(t("start_welcome", settings.default_lang), reply_markup=lang_choice())

@router.callback_query(F.data.startswith("lang:"))
async def set_lang(cb: types.CallbackQuery, state: FSMContext):
    lang = cb.data.split(":")[1]
    await state.update_data(lang=lang)
    await cb.message.answer(t("ask_fullname", lang))
    await state.set_state(Register.full_name)
    await cb.answer()

@router.message(Register.full_name)
async def ask_contact(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", settings.default_lang)
    await state.update_data(full_name=message.text.strip())
    await message.answer(t("ask_contact", lang), reply_markup=request_contact_kb(lang))
    await state.set_state(Register.contact)

@router.message(Register.contact, F.contact)
async def save_user(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", settings.default_lang)
    full_name = data.get("full_name", message.from_user.full_name or "")
    phone = message.contact.phone_number if message.contact else ""
    username = message.from_user.username or ""

    await upsert_user(
        tg_id=message.from_user.id,
        full_name=full_name,
        username=username,
        phone=phone,
        language=lang
    )

    # Trail reset va asosiy menyu
    await state.update_data(trail=["root"])
    await message.answer(t("saved", lang), reply_markup=main_menu(lang))
    await state.clear()
