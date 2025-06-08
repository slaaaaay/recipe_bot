from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
from config.settings import bot_token
from middlewares.throttling import ThrottlingMiddleware

from routers import commands, handlers
from logs.logger import setup_logger

async def main():
    setup_logger()
    bot = Bot(token=bot_token)
    dp = Dispatcher(storage=MemoryStorage())

    dp.message.middleware.register(ThrottlingMiddleware())

    dp.include_router(commands.router)
    dp.include_router(handlers.router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())