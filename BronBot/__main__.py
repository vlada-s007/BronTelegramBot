import asyncio
import logging

from decouple import config

from aiogram import Bot, Dispatcher

from BronBot.handlers import base_router
from BronBot.handlers import auth_router
from BronBot.handlers import booking_router
from BronBot.handlers import payment_router
from BronBot.middlewares import init_pool, close_pool
from BronBot.middlewares import i18n_middleware
from BronTelegramBot.utils import scheduler


async def main():
    logging.basicConfig(level=logging.DEBUG)
    # logging.getLogger('apscheduler').setLevel(logging.DEBUG)
    token = config('TOKEN')

    # for pythonanywhere
    # session = AiohttpSession(proxy="http://proxy.server:3128")
    # bot = Bot(token, session=session)

    bot = Bot(token)

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
