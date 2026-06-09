from datetime import datetime
from typing import Callable, Dict, Any, Awaitable, Union

import orjson
from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.client.session.aiohttp import AiohttpSession, ClientSession
import asyncio

from aiohttp import BasicAuth
from passlib.hash import pbkdf2_sha256

from asyncpg import Connection

from bronTelegramBot.states import UserState


class AuthMiddleware(BaseMiddleware):

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Union[Message, CallbackQuery],
            data: Dict[str, Any]
    ) -> Any:
        # conn: Connection = data['connect']
        state: FSMContext = data['state']
        session: ClientSession = data['session']
        base_url = 'http://127.0.0.1:8000'
        state_data = await state.get_data()

        if event.contact and not state_data.get('auth'):
            chat_id = event.chat.id
            telegram_id = event.from_user.id
            phone = event.contact.phone_number

            async with session:
                async with session.post(f'{base_url}/api/users/telegram/connect',
                                        json={'phone': phone}) as response:
                    print(response.status)
                    data_resp = await response.json()
                    print('data access', data_resp)
                    headers = {'Authorization': f'Bearer {data_resp["access_token"]}'}
                    async with session.put(f'{base_url}/api/users/profile/telegram', headers=headers,
                                            json={'telegram_id': telegram_id}) as response:
                        print(response.status)
                        data_put = await response.json()
                        print(data_put)
                        await state.update_data(auth=data_resp)
        elif state_data.get('auth'):
            print('Пользователь уже зарегестрирован')
                # username = event.from_user.username
                # first_name = event.contact.first_name
                # language = state_data['locale']
            #     print(language)
            #     async with conn.transaction():
            #         await conn.transaction().start()
            #         await conn.execute('''INSERT INTO
            #         core_user(is_superuser, is_staff, is_active, is_verified, role, language,  phone, telegram_id, username, first_name, date_joined, created_at)
            #         VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)''',
            #                            False, False, True, False, 'customer', language, phone, chat_id, str(username), first_name, datetime.now(),
            #                            datetime.now())
            #     last_name = event.contact.last_name
            #     if last_name:
            #         await state.update_data(last_name=last_name)
            #         async with conn.transaction():
            #             await conn.execute('INSERT INTO core_user(first_name) VALUES($1) WHERE telegram_id = $2',
            #                                last_name, chat_id)
            #             await conn.transaction().commit()
            # print(await state.get_data())
            # await conn.close()
        return await handler(event, data)
