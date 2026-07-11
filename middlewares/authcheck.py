import datetime
from datetime import timedelta

from aiogram.client.bot import Bot
from decouple import config
from typing import Callable, Dict, Any, Awaitable, Union
from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.client.session.aiohttp import AiohttpSession, ClientSession
from aiogram import html
from aiogram.utils.i18n import gettext as _
from BronTelegramBot.middlewares.database import search_user_by_tg_id, update_database_tg_id, \
    search_bookings_for_profile, get_booking_details, service_title_duration_and_price_by_id, business_name_by_id, \
    get_branch_info_by_id
from BronTelegramBot.utils import scheduler
from BronTelegramBot.utils import text_to_datetime, combine_time

# for pythonanywhere
session = AiohttpSession(proxy="http://proxy.server:3128")
token = config('TOKEN')
bot = Bot(token=token, session=session)

# token = config('TOKEN')
# bot = Bot(token)

class AuthMiddleware(BaseMiddleware):

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Union[Message, CallbackQuery],
            data: Dict[str, Any]
    ) -> Any:
        state: FSMContext = data['state']
        state_data = await state.get_data()
        telegram_id = event.from_user.id
        user_database_id = await search_user_by_tg_id(telegram_id)
        try:
            chat_id = event.chat.id
        except:
            chat_id = event.message.chat.id
        if event.contact and not state_data.get('auth') and not user_database_id:
            phone = event.contact.phone_number
            if not phone.startswith('+'):
                phone = '+' + phone
            print('phone' + phone)
            print('tg_id' + str(telegram_id))
            base_url = config('base_url')
            # for pythonanywhere
            # session = ClientSession(base_url=base_url, proxy="http://proxy.server:3128")

            session = ClientSession(base_url=base_url)

            async with session:
                async with session.post(f'users/telegram/connect',
                                        json={'phone': phone}) as response:
                    print(response.status)
                    try:
                        data_resp = await response.json()
                        print(data_resp)
                        json_data = {'telegram_id': telegram_id}
                        auth = f'Bearer {data_resp["access_token"]}'
                        if response.status != 200:
                            return await handler(event,data)
                    except:
                        data_resp = await response.text()
                        print(data_resp)
                        await state.clear()
                        return await handler(event, data)
                    # handling any scenario
                session.headers['Authorization'] = auth
                async with session.put(f'users/profile/telegram', json=json_data) as response:
                    print(response.status)
                    try:
                        register_resp = await response.json()
                    except:
                        register_resp = await response.text()
                    print(register_resp)
                    await state.clear()
                    await state.update_data(user_id=data_resp['user_id'])
                    await state.update_data(notifications=True)
                    await state.update_data(chat_id=event.chat.id)
                    # only for local database, remove when production is over
                    await update_database_tg_id(telegram_id, data_resp['user_id'])
                    print('database login added')
        elif state_data.get('user_id'):
            print('User is already authenticated')
        elif user_database_id and not state_data.get('user_id'):
            await state.clear()
            await state.update_data(notifications=True)
            await state.update_data(chat_id=chat_id)
            state_data = await state.update_data(user_id=user_database_id[0])
            # await self.create_upcoming_notification(user_database_id[0], chat_id)
        if not state_data.get('notifications'):
            await state.update_data(notifications=True)
            await state.update_data(chat_id=chat_id)
        return await handler(event, data)