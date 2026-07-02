from aiogram import Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram import html
from aiogram.utils.i18n import gettext as _
# from BronTelegramBot.middlewares.locales import i18n, i18n_middleware
from decouple import config

from BronTelegramBot.keyboards.keyboard_base import language_inline, main_menu, back_to_main_menu_button
from BronTelegramBot.middlewares.locales import i18n_middleware

base_router = Router()
token = config('TOKEN')
bot = Bot(token)

@base_router.callback_query(lambda call: 'base_router_main_menu' in call.data)
async def get_main_menu(call:CallbackQuery, state: FSMContext):
    state = await state.get_data()
    print(state)
    try:
        await call.message.edit_text(_('Welcome to Bron. Choose your actions:'), reply_markup=await main_menu())
    except:
        await call.message.answer(_('Welcome to Bron. Choose your actions:'), reply_markup=await main_menu())


@base_router.callback_query(lambda call: 'chooseLocale' in call.data)
async def choose_language_menu(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(_('Choose your language:'), reply_markup=language_inline)


@base_router.callback_query(lambda call: 'lang' in call.data)
async def set_language(call: CallbackQuery, state: FSMContext):
    lang = call.data.split('_')[-1]
    await i18n_middleware.set_locale(state, lang)
    await bot.answer_callback_query(call.id, _('Language set successfully.'))
    try:
        await call.message.edit_text(_('Welcome to Bron. Choose your actions:'), reply_markup=await main_menu())
    except:
        await call.message.answer(_('Welcome to Bron. Choose your actions:'), reply_markup=await main_menu())


@base_router.callback_query(lambda call: 'help' in call.data)
async def help_command(call: CallbackQuery):
    await call.message.edit_text(_('In development'), reply_markup=await back_to_main_menu_button())


@base_router.callback_query(lambda call: 'about' in call.data)
async def help_command(call: CallbackQuery):
    await call.message.edit_text(_('In development'), reply_markup=await back_to_main_menu_button())

@base_router.callback_query(lambda call: 'profile' in call.data)
async def help_command(call: CallbackQuery):
    await call.message.edit_text(_('In development'), reply_markup=await back_to_main_menu_button())

@base_router.callback_query(lambda call: 'mainMenu' in call.data)
async def help_command(call: CallbackQuery):
    await call.message.edit_text(_('Choose your actions:'), reply_markup=await main_menu())


