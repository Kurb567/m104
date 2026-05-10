import asyncio
from aiogram import Bot, Dispatcher, html
from app.handlers import router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from check_pay_last_hour import *
import config as x


TOKEN = x.TOKEN
dp = Dispatcher()


async def main():
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp.include_router(router)
    await dp.start_polling(bot)
    while True:
        await run_sync()
        await asyncio.sleep(60)  # Проверять каждые 5 минут
    


if __name__ == "__main__":
    asyncio.run(main())


