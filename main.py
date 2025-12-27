import asyncio
from aiogram import Bot, Dispatcher, html
from app.handlers import router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
import config as x


TOKEN = x.TOKEN
dp = Dispatcher()


async def main():
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp.include_router(router)
    await dp.start_polling(bot)
    


if __name__ == "__main__":
    asyncio.run(main())
     
