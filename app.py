import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from config import settings
from database import init_db
from handlers import start, menu, services, partner, admin

async def main():
    await init_db()
    bot = Bot(settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(start.router)
    dp.include_router(menu.router)
    dp.include_router(services.router)
    dp.include_router(partner.router)
    dp.include_router(admin.router)

    print("[CONFIG] BOT_TOKEN loaded:", bool(settings.bot_token))
    print("[CONFIG] DATABASE_URL:", settings.database_url)
    print("[CONFIG] ADMIN_IDS:", settings.admin_ids)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
