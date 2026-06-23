import json
from decouple import config
from datetime import datetime
from typing import Callable, Dict, Any, Awaitable, Union

from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.client.session.aiohttp import AiohttpSession, ClientSession
import asyncio

from aiohttp import BasicAuth
from passlib.hash import pbkdf2_sha256

from asyncpg import Connection

from bronTelegramBot.middlewares.database import search_user_by_tg_id
from bronTelegramBot.states import UserState


class AuthMiddleware(BaseMiddleware):

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Union[Message, CallbackQuery],
            data: Dict[str, Any]
    ) -> Any:
        state: FSMContext = data['state']
        # session: ClientSession = data['session'])
        state_data = await state.get_data()
        telegram_id = event.from_user.id
        user_database_id = await search_user_by_tg_id(telegram_id)
        if event.contact and not state_data.get('auth') and not user_database_id:
            chat_id = event.chat.id
            phone = event.contact.phone_number
            session = ClientSession(config='base_url')
            async with session:
                async with session.post(f'users/telegram/connect',
                                        json={'phone': phone}) as response:
                    print(response.status)
                    data_resp = await response.json()
                    print(data_resp)
                    json_data = {'telegram_id': telegram_id}
                    auth = f'Bearer {data_resp["access_token"]}'
                    tg = f'{data_resp["tg_token"]}'
                session.headers['Authorization'] = auth
                session.headers['TelegramToken'] = tg
                async with session.put(f'users/profile/telegram', json=json_data) as response:
                    print(response.status)
                    try:
                        register_resp = await response.json()
                    except:
                        register_resp = await response.text()
                    print(register_resp)
                    await state.clear()
                    await state.update_data(user_id=data_resp['user_id'])
        elif state_data.get('user_id'):
            print('Пользователь уже зарегестрирован')
        elif user_database_id and not state_data.get('user_id'):
            await state.clear()
            state_data = await state.update_data(user_id=user_database_id)
            print(state_data)
        return await handler(event, data)
