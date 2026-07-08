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

class NotificationMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Union[Message, CallbackQuery],
            data: Dict[str, Any]
    ) -> Any:
        state: FSMContext = data['state']
        state_data = await state.get_data()

        if state_data.get('user_id') and state_data.get('chat_id') and state_data.get('notifications'):
            chat_id = state_data['chat_id']
            user_id = state_data['user_id']
            reservations = await search_bookings_for_profile(user_id, "confimed", "pending")
            reservation_ids = [reservation[0] for reservation in reservations]
            for reservation in reservations:
                if reservation[0] in reservation_ids and state_data['notifications'] is True:
                    start_time = text_to_datetime(reservation[1], "%H:%M:%S")
                    date = text_to_datetime(reservation[3], "%Y-%m-%d")
                    start_time_str = ':'.join(reservation[1].split(':')[:-1])
                    end_time_str = ':'.join(reservation[2].split(':')[:-1])
                    time = f'{start_time_str} - {end_time_str}'
                    datetime_format = combine_time(date, (start_time - timedelta(hours=1)).time())
                    print(datetime_format, 'datetime_for_notifs')

                    reservation_info = await get_booking_details(reservation[0])

                    business_name = await business_name_by_id(reservation_info[1])
                    service_title = await service_title_duration_and_price_by_id(reservation_info[2])
                    branch_name = await get_branch_info_by_id(reservation_info[3])
                    scheduler.add_job(
                        self.send_notification,
                        trigger="date", run_date=datetime_format, args=[chat_id, time, business_name, service_title[0], branch_name[1]])
                    reservation_ids.remove(reservation[0])
        elif state_data.get('notifications'):
            scheduler.remove_all_jobs()
        return await handler(event, data)
    async def send_notification(self, chat_id, time, business_name, service_title, branch_name):
        await bot.send_message(chat_id=chat_id, text=_(
            'You have a {time} reservation at {business_name} - {branch_name}" for "{service_title}", in an hour!'
        ).format(time=html.quote(time), business_name=html.quote(business_name),
            service_title=html.quote(service_title), branch_name=html.quote(branch_name)))
