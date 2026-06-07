# Будет реализована после оформления API на авторизацию
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
from bronTelegramBot.keyboard.markups import language_inline, send_contact


token = config('TOKEN')
bot = Bot(token)
auth_router = Router()

auth_router.message.middleware(AuthMiddleware())


@auth_router.message(Command('start'))
async def command_start(message: Message, state: FSMContext):
    data = await state.get_data()
    user = data.get('user_database')
    await state.update_data(telegram_id=message.chat.id)
    print('fsm state', data)
    print('user_database', user)

    if not user:
        print(f'lang_code {message.from_user.language_code}')
        lang_code = message.from_user.language_code
        try:
            await i18n_middleware.set_locale(state, lang_code)
            await state.update_data(user_language=lang_code)

        except:
            await i18n_middleware.set_locale(state, 'en')
            await state.update_data(user_language='en')

        text = await get_text()
        await message.answer(_('Welcome to Bron, {username}. You are currently not logged in.\nShare contact information in order to log in or register:').format(
            username=html.quote(message.from_user.username)), reply_markup=await send_contact(text))
        await state.set_state(UserState.phone)



    else:
        # username = user[4]
        # lang = user[-3]
        await state.update_data(user_database=user)


@auth_router.message(F.contact)
async def register_user(message: Message, state: FSMContext):
    # first_name = message.contact.first_name
    # last_name = message.contact.last_name
    # phone = message.contact.phone_number
    # if first_name:
    #     await state.update_data(first_name=first_name)
    # if last_name:
    #     await state.update_data(last_name=last_name)
    # data = await state.update_data(phone=phone)
    # locale = data['locale']
    # await state.clear()
    # await i18n_middleware.set_locale(state, locale)
    await message.answer(_('Registration is completed!'))

async def get_text():
    text = _('Share contact information')
    return text
