import asyncio
import logging

import asyncpg
from decouple import config

from aiogram import Bot, Dispatcher

from redis.asyncio import Redis
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.client.session.aiohttp import AiohttpSession, ClientSession

from bronTelegramBot.handlers.base import base_router
from bronTelegramBot.handlers.auth import auth_router
from bronTelegramBot.handlers.booking import booking_router
from bronTelegramBot.middlewares.locales import i18n_middleware


async def main():
    logging.basicConfig(level=logging.DEBUG)
    token = config('TOKEN')
    bot = Bot(token)

    # redis = Redis()
    # storage = RedisStorage(redis=redis)
    # dp = Dispatcher(bot=bot, storage=storage)

    dp = Dispatcher(bot=bot)

    i18n_middleware.setup(dp)
    # session = ClientSession()

    # asyncpg connect
    # database = config('DB_NAME')
    # user = config('DB_USER')
    # password = config('DB_PASSWORD')
    # host = config('DB_HOST')
    # port = config('DB_PORT')
    # conn = await asyncpg.connect(
    #     host=str(host),
    #     port=str(port),
    #     password=str(password),
    #     database=str(database),
    #     user=str(user))

    #aiosqlite connect


    dp.include_router(auth_router)
    dp.include_router(base_router)
    dp.include_router(booking_router)

    # await dp.start_polling(bot, connect=conn, session=session)
    # await dp.start_polling(bot, session=session)
    await dp.start_polling(bot)




if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print('Bot terminated')
