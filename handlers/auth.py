# Будет реализована после оформления API на авторизацию
import orjson
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram import html
from aiogram.utils.i18n import gettext as _

from bronTelegramBot.markups import send_contact



auth_router = Router()


# class UserState(StatesGroup):
#     telegram_id = State()
#     phone = State()
#     access_token = State()
#     refresh_token = State()
#
# # Позже добавить middleware, которая будет посылать запрос на авторизацию
# @base_router.message(Command('start'))
# async def command_start(message: Message, state: FSMContext):
#     user = await telegram_id_exists(message.chat.id)
#     await state.set_state(UserState.telegram_id)
#     await state.update_data(telegram_id=message.chat.id)
#     if not user:
#         text = await get_text()
#         await message.answer(_('Share contact information in order to complete registration'),
#                              reply_markup=await send_contact(text))
#         await state.set_state(UserState.phone)
#
#     else:
#         # Метод авторизации будет сделан, как только будут оформлены API
#         await message.answer(f'''Welcome to Bron, {message.from_user.username}. Choose your language: ''',
#                              reply_markup=language_inline)
#
#
# @auth_router.message(F.contact)
# async def register_user(message:Message, state: FSMContext):
#     data = await state.update_data(phone=message.contact.phone_number)
#     json = orjson.dumps(data)
#
#
# async def get_text():
#     text = _('Share contact information')
#     return text
