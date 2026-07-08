import asyncio
import logging

from aiogram import Bot, Dispatcher

from config import BOT_TOKEN
from handlers import start, add, view


async def main():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(start.router)
    dp.include_router(add.router)
    dp.include_router(view.router)

    from db import init_db

    await init_db()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
