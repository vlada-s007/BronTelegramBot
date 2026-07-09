from aiogram import Router, Bot, F
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.context import FSMContext
import asyncio
from BronTelegramBot.middlewares.authcheck import AuthMiddleware
from BronTelegramBot.middlewares.locales import i18n_middleware
from BronTelegramBot.middlewares.notification_middleware import NotificationMiddleware
from BronTelegramBot.states import UserState
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram import html
from aiogram.utils.i18n import gettext as _
from decouple import config
from BronTelegramBot.keyboards.keyboard_base import send_contact, main_menu, continue_button

# for pythonanywhere
session = AiohttpSession(proxy="http://proxy.server:3128")
token = config('TOKEN')
bot = Bot(token=token, session=session)

# token = config('TOKEN')
# bot = Bot(token)

auth_router = Router()
auth_router.message.middleware(AuthMiddleware())
auth_router.message.middleware(NotificationMiddleware())


@auth_router.message(Command('start'))
async def command_start(message: Message, state: FSMContext):
    state_data = await state.get_data()
    if not state_data.get('user_id'):
        lang_code = message.from_user.language_code
        try:
            await i18n_middleware.set_locale(state, lang_code)
            await state.update_data(user_language=lang_code)
        except:
            await i18n_middleware.set_locale(state, 'en')
            await state.update_data(user_language='en')
        await message.answer(_('Welcome to Bron. You are currently not logged in.\nShare contact information in order to log in or register:'), reply_markup=await send_contact())
        await state.update_data(telegram_id=message.chat.id)
        await state.set_state(UserState.phone)
        await state.set_state(UserState.user_id)
    else:
        await message.answer(_('You are already logged in.'), reply_markup=await continue_button())


@auth_router.message(UserState.user_id)
async def authorize_user(message: Message, state: FSMContext):
    data = await state.get_data()
    if data.get('user_id'):
        await message.answer(_('Registration is completed!'), reply_markup=await continue_button())
    elif not data.get('user_id'):
        await message.answer(_('''This is a test message: if you are seeing this, the app is still in development.
        There is no account with your phone number registered on the database. Sign up on the website: {website}'''
                               ).format(website=html.quote('https://uzbalpha.pythonanywhere.com/api/')))
