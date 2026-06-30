from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import html
from aiogram.utils.i18n import gettext as _

language_inline = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='UZ 🇺🇿', callback_data='lang_uz'),
     InlineKeyboardButton(text='ENG 🇬🇧🇺🇸', callback_data='lang_eng'),
     InlineKeyboardButton(text='RU 🇷🇺', callback_data='lang_ru')]]
)


async def send_contact():
    markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=_('Share contact information'), request_contact=True
                                                           )]], resize_keyboard=True)
    return markup


async def continue_button():
    markup = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=_('Continue'), callback_data='base_router_main_menu')]])
    return markup


async def main_menu():
    builder = InlineKeyboardBuilder()

    builder.button(text='📋 '+ _('Booking...'), callback_data='bookingMenu')
    builder.button(text='👤 '+ _('My Profile'), callback_data='profile')
    builder.button(text='🌐 ' + _('Change Language'), callback_data='chooseLocale')
    builder.button(text='ℹ️ ' + _('About Bron'), callback_data='about')
    builder.button(text='🆘 ' + _('Help'), callback_data='help'),
    builder.adjust(1, 1, 1, 1, 1)
    return builder.as_markup()

async def back_to_main_menu_button():
    back_button = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='⫶☰ ' + _('Back to Main Menu'), callback_data='mainMenu')]]
    )
    return back_button




