import asyncio
import logging

from redis.asyncio import Redis
from aiogram.fsm.storage.redis import RedisStorage
from decouple import config

from aiogram import Bot, Dispatcher

from aiogram.client.session.aiohttp import AiohttpSession
from BronTelegramBot.handlers.base import base_router
from BronTelegramBot.handlers.auth import auth_router
from BronTelegramBot.handlers.booking import booking_router
from BronTelegramBot.handlers.payment import payment_router
from BronTelegramBot.middlewares.database import init_pool, close_pool
from BronTelegramBot.middlewares.locales import i18n_middleware
from BronTelegramBot.utils import scheduler


async def main():
    logging.basicConfig(level=logging.DEBUG)
    # logging.getLogger('apscheduler').setLevel(logging.DEBUG)
    token = config('TOKEN')

    # for pythonanywhere
    session = AiohttpSession(proxy="http://proxy.server:3128")
    bot = Bot(token, session=session)

    # bot = Bot(token)

    dp = Dispatcher(bot=bot)
    scheduler.start()
    i18n_middleware.setup(dp)

    # asyncpg connection pool.
    pool = await init_pool()
    dp['pool'] = pool

    dp.include_router(auth_router)
    dp.include_router(base_router)
    dp.include_router(booking_router)
    dp.include_router(payment_router)

    try:
        await dp.start_polling(bot)
    finally:
        scheduler.shutdown(wait=False)
        await close_pool()
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print('Bot terminated')
