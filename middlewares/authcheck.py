#
# from datetime import datetime
# from typing import Callable, Dict, Any, Awaitable, Union
#
# import orjson
# from aiogram import BaseMiddleware
# from aiogram.fsm.context import FSMContext
# from aiogram.types import Message, CallbackQuery
# from aiogram.client.session.aiohttp import AiohttpSession, ClientSession
# import asyncio
#
# from aiohttp import BasicAuth
# from passlib.hash import pbkdf2_sha256
#
# from asyncpg import Connection
#
# from bronTelegramBot.states import UserState
#
#
# class AuthMiddleware(BaseMiddleware):
#
#     async def __call__(
#             self,
#             handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
#             event: Union[Message, CallbackQuery],
#             data: Dict[str, Any]
#     ) -> Any:
#         conn: Connection = data['connect']
#         state: FSMContext = data['state']
#         session: ClientSession = data['session']
#         base_url = 'http://127.0.0.1:8000/api'
#         state_data = await state.get_data()
#         if state_data.get('user_database'):
#             user_id = state_data['user_database']
#             user = await conn.fetchrow('''SELECT id, password, username, first_name, last_name FROM core_user
#                         WHERE id = $1::int ''', user_id)
#             print(user)
#
#             await state.update_data(user_database=user[0])
#             password = user[1]
#             username = user[2]
#             print(password, username)
#             print(session)
#             async with session:
#                 async with session.post(f'{base_url}/auth/login',
#                                         json={'username': username, 'password': password}) as response:
#                     print(response.status)
#                     print(response.json())
#
#             # get access token somehow
#             return await handler(event, data)
#
#         else:
#             telegram_id = event.from_user.id
#             user = await conn.fetchrow('''SELECT id, password, username, first_name, last_name FROM core_user
#             WHERE telegram_id = $1::int ''', telegram_id)
#             if user:
#                 base_url = 'http://127.0.0.1:8000/api'
#                 await state.update_data(user_database=user[0])
#                 password = user[1]
#                 username = user[2]
#                 print(password, username)
#                 print(session)
#                 async with session:
#                     async with session.post(f'{base_url}/auth/login',
#                                             json={'username': username, 'password': password}) as response:
#                         print(response.status)
#                         print(response.json(loads=orjson.loads()))
#                         # access = orjson.loads(json_response)
#                         # print(access)
#                 # get access token somehow
#             if event.contact and not user:
#                 phone = event.contact.phone_number
#                 # await state.update_data(phone=phone)
#                 user_only_phone = await conn.fetchrow('SELECT id, password, username, first_name, last_name FROM core_user  FROM core_user WHERE phone = $1', phone)
#                 if user_only_phone:
#                     await state.update_data(user_only_phone=user[0])
#                     await conn.execute('''UPDATE core_user SET telegram_id = $1 WHERE id=$2''',
#                                        telegram_id, user_only_phone[0])
#                 else:
#                     pass
#                     # username = event.from_user.username
#                     # first_name = event.contact.first_name
#                     # language = state_data['locale']
#                 #     print(language)
#                 #     async with conn.transaction():
#                 #         await conn.transaction().start()
#                 #         await conn.execute('''INSERT INTO
#                 #         core_user(is_superuser, is_staff, is_active, is_verified, role, language,  phone, telegram_id, username, first_name, date_joined, created_at)
#                 #         VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)''',
#                 #                            False, False, True, False, 'customer', language, phone, chat_id, str(username), first_name, datetime.now(),
#                 #                            datetime.now())
#                 #     last_name = event.contact.last_name
#                 #     if last_name:
#                 #         await state.update_data(last_name=last_name)
#                 #         async with conn.transaction():
#                 #             await conn.execute('INSERT INTO core_user(first_name) VALUES($1) WHERE telegram_id = $2',
#                 #                                last_name, chat_id)
#                 #             await conn.transaction().commit()
#                 # print(await state.get_data())
#                 await conn.close()
#             return await handler(event, data)
