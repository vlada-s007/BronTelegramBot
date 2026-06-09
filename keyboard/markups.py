from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.i18n import lazy_gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder


language_inline = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='UZ 🇺🇿', callback_data='lang_uz'),
     InlineKeyboardButton(text='ENG 🇬🇧🇺🇸', callback_data='lang_eng'),
     InlineKeyboardButton(text='RU 🇷🇺', callback_data='lang_ru')]]
)


async def send_contact(text):
    markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=text, request_contact=True
                                                             )]], resize_keyboard=True)
    return markup

async def continue_button(text):
    markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=text, callback_data='base_router_main_menu')]])
    return markup

async def main_menu(*args):
    builder = InlineKeyboardBuilder()
    builder.button(text=str(args[0]), callback_data='bookingMenu')
    builder.button(text=str(args[1]), callback_data='profile')
    builder.button(text=str(args[2]), callback_data='chooseLocale')
    builder.button(text=str(args[3]), callback_data='about')
    builder.button(text=str(args[4]), callback_data='help'),
    builder.adjust(1, 1, 1, 1, 1)
    markup = builder.as_markup()
    return markup


back_button = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='<-', callback_data='mainMenu')]]
)

async def booking_menu_markup(*args):
    builder = InlineKeyboardBuilder()
    builder.button(text=str(args[0]), callback_data='categoryChoose')
    builder.button(text=str(args[1]), callback_data='searchBooking')
    builder.button(text='<-', callback_data='mainMenu')
    builder.adjust(1, 1, 1)
    markup = builder.as_markup()
    return markup


