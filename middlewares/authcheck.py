import datetime
from datetime import timedelta

from aiogram.client.bot import Bot
from decouple import config
from typing import Callable, Dict, Any, Awaitable, Union
from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.client.session.aiohttp import ClientSession
from aiogram import html
from aiogram.utils.i18n import gettext as _
from BronTelegramBot.middlewares.database import search_user_by_tg_id, update_database_tg_id, \
    search_bookings_for_profile, get_booking_details, service_title_duration_and_price_by_id, business_name_by_id, \
    get_branch_info_by_id
from BronTelegramBot.utils import scheduler
from BronTelegramBot.utils import text_to_datetime, combine_time

# for pythonanywhere
# session = AiohttpSession(proxy="http://proxy.server:3128")
# token = config('TOKEN')
# bot = Bot(token=token, session=session)

token = config('TOKEN')
bot = Bot(token)

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
                    await update_database_tg_id(telegram_id, data_resp['user_id'])
                    # await self.create_upcoming_notification(data_resp['user_id'], chat_id)


# only for local database, remove when production is over
                    print('database login added')
        elif state_data.get('user_id'):
            print('User is already authenticated')
            # await self.create_upcoming_notification(state_data['user_id'], chat_id)
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
    # if event.contact and not state_data.get('auth'):
    #     chat_id = event.chat.id
    #     phone = event.contact.phone_number
    #     base_url = config('base_url')
    #     session = ClientSession(base_url=base_url)
    #     async with session:
    #         async with session.post(f'users/telegram/connect',
    #                                 json={'phone': phone}) as response:
    #             print(response.status)
    #             data_resp = await response.json()
    #             print(data_resp)
    #             json_data = {'telegram_id': telegram_id}
    #             auth = f'Bearer {data_resp["access_token"]}'
    #             tg = f'{data_resp["tg_token"]}'
    #         session.headers['Authorization'] = auth
    #         session.headers['TelegramToken'] = tg
    #         async with session.put(f'users/profile/telegram', json=json_data) as response:
    #             print(response.status)
    #             try:
    #                 register_resp = await response.json()
    #             except:
    #                 register_resp = await response.text()
    #             print(register_resp)
    #             await state.clear()
    #             await state.update_data(user_id=data_resp['user_id'])
    # elif state_data.get('user_id'):
    #     print('Пользователь уже зарегестрирован')
    # # elif user_database_id and not state_data.get('user_id'):
    # #     await state.clear()
    # #     state_data = await state.update_data(user_id=user_database_id)
    # #     print(state_data)
    # return await handler(event, data)

    # async def create_upcoming_notification(self, user_id, chat_id):
    #     reservations = await search_bookings_for_profile(user_id, "confimed", "pending")
    #     for reservation in reservations:
    #         start_time = text_to_datetime(reservation[1], "%H:%M:%S")
    #         date = text_to_datetime(reservation[3], "%Y-%m-%d")
    #         start_time_str = ':'.join(reservation[1].split(':')[:-1])
    #         end_time_str = ':'.join(reservation[2].split(':')[:-1])
    #         time = f'{start_time_str} - {end_time_str}'
    #         datetime_format = combine_time(date, (start_time - timedelta(hours=1)).time())
    #         print(datetime_format, 'datetime_for_notifs')
    #
    #         reservation_info = await get_booking_details(reservation[0])
    #
    #         business_name = await business_name_by_id(reservation_info[1])
    #         service_title = await service_title_duration_and_price_by_id(reservation_info[2])
    #         branch_name = await get_branch_info_by_id(reservation_info[3])
    #         scheduler.add_job(
    #             self.send_notification,
    #             trigger="date", run_date=datetime_format, args=[chat_id, time, business_name, service_title[0], branch_name[1]])
    #
    # async def send_notification(self, chat_id, time, business_name, service_title, branch_name):
    #
    #     await bot.send_message(chat_id=chat_id, text=_(
    #         'You have a {time} reservation at {business_name} - {branch_name}" for "{service_title}", in an hour!'
    #     ).format(time=html.quote(time), business_name=html.quote(business_name),
    #         service_title=html.quote(service_title), branch_name=html.quote(branch_name)))
