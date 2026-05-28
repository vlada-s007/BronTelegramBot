import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage

from decouple import config
from redis.asyncio import Redis

from bronTelegramBot.handlers.base import base_router
from bronTelegramBot.handlers.auth import auth_router
import logging
from bronTelegramBot.handlers.booking import booking_router
from bronTelegramBot.middlewares.locales import i18n_middleware


async def main():
    logging.basicConfig(level=logging.DEBUG)
    token = config('TOKEN')
    bot = Bot(token)
    # dp.include_router(auth_router)
    redis = Redis()
    dp = Dispatcher(bot=bot, storage=RedisStorage(redis=redis))
    dp.include_router(base_router)
    dp.include_router(booking_router)
    i18n_middleware.setup(dp)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print('Bot terminated')
