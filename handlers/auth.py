from aiogram import Router, Bot, F
from aiogram.fsm.context import FSMContext
import asyncio

from bronTelegramBot.middlewares.authcheck import AuthMiddleware
from bronTelegramBot.middlewares.locales import i18n_middleware
from bronTelegramBot.states import UserState, LangState, TempMessageState
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram import html
from aiogram.utils.i18n import gettext as _
from decouple import config
from bronTelegramBot.keyboard.markups import language_inline, send_contact, main_menu, continue_button

token = config('TOKEN')
bot = Bot(token)
auth_router = Router()


auth_router.message.middleware(AuthMiddleware())


@auth_router.message(Command('start'))
async def command_start(message: Message, state: FSMContext):
    lang_code = message.from_user.language_code
    try:
        await i18n_middleware.set_locale(state, lang_code)
        await state.update_data(user_language=lang_code)
    except:
        await i18n_middleware.set_locale(state, 'en')
        await state.update_data(user_language='en')

    text = await get_text_contact_button()
    await message.answer(
        _('Welcome to Bron, {username}. You are currently not logged in.\nShare contact information in order to log in or register:').format(
            username=html.quote(message.from_user.username)), reply_markup=await send_contact(text))
    await state.update_data(telegram_id=message.chat.id)
    await state.set_state(UserState.phone)
    await state.set_state(UserState.auth)


@auth_router.message(UserState.auth)
async def authorize_user(message: Message, state: FSMContext):
    data = await state.get_data()
    if data.get('auth'):
        print(data.get('auth'))
        text = await get_text_continue_button()
        await message.answer(_('Registration is completed!'), reply_markup=await continue_button(text))


async def get_text_contact_button():
    text = _('Share contact information')
    return text

async def get_text_continue_button():
    text = _('Continue')
    return text
