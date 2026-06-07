# Авторизация будет реализована после оформления API на авторизацию, это базовый тест
from aiogram import Router, Bot
from aiogram.fsm.context import FSMContext
from bronTelegramBot.states import LangState
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram import html
from aiogram.utils.i18n import gettext as _
# from bronTelegramBot.middlewares.locales import i18n, i18n_middleware
from decouple import config

from bronTelegramBot.keyboard.markups import language_inline, main_menu, back_button
from bronTelegramBot.middlewares.locales import i18n_middleware

base_router = Router()
token = config('TOKEN')
bot = Bot(token)



@base_router.callback_query(lambda call: 'lang' in call.data)
async def set_language(call: CallbackQuery, state: FSMContext):
    lang = call.data.split('_')[-1]
    data = await state.update_data(lang=lang)
    await i18n_middleware.set_locale(state, data['lang'])
    await bot.answer_callback_query(call.id, _('Language set successfully.'))
    args = await get_main_menu_text()
    await call.message.edit_text(_('Choose your actions:'), reply_markup=await main_menu(*args))


@base_router.callback_query(lambda call: 'chooseLocale' in call.data)
async def choose_language_menu(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(_('Choose your language:'), reply_markup=language_inline)
    await state.set_state(LangState.lang)


async def get_main_menu_text():
    book = _('Booking...')
    profile = _('My Profile')
    language = _('Change Language')
    about = _('About Bron')
    help_section = _('Help')
    return book, profile, language, about, help_section


@base_router.callback_query(lambda call: 'help' in call.data)
async def help_command(call: CallbackQuery):
    await call.message.edit_text(_('In development'), reply_markup=back_button)


@base_router.callback_query(lambda call: 'about' in call.data)
async def help_command(call: CallbackQuery):
    await call.message.edit_text(_('In development'), reply_markup=back_button)

@base_router.callback_query(lambda call: 'profile' in call.data)
async def help_command(call: CallbackQuery):
    await call.message.edit_text(_('In development'), reply_markup=back_button)

@base_router.callback_query(lambda call: 'mainMenu' in call.data)
async def help_command(call: CallbackQuery):
    args = await get_main_menu_text()
    await call.message.edit_text(_('Choose your actions:'), reply_markup=await main_menu(*args))


