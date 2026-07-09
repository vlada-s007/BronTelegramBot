from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import html
from aiogram.utils.i18n import gettext as _
from datetime import datetime
from babel.dates import format_date
from babel.numbers import format_currency

from BronTelegramBot.middlewares.database import service_title_duration_and_price_by_id

language_inline = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='UZ 🇺🇿', callback_data='lang_uz'),
     InlineKeyboardButton(text='ENG 🇬🇧🇺🇸', callback_data='lang_eng'),
     InlineKeyboardButton(text='RU 🇷🇺', callback_data='lang_ru')]]
)


async def send_contact():
    markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=_('Share contact information'), request_contact=True
                                                           )]], resize_keyboard=True)
    return markup

start_inline = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='/start')]]
)


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

async def profile_view_buttons(state: dict):
    if state.get('notifications'):
        notif_state = state['notifications']
        if notif_state is True:
            notif_text = '🔔 ' + _('Notifications') + ' ' + _('ON')
        else:
            notif_text = '🔕 ' + _('Notifications') + ' ' + _('OFF')
    back_button = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🗓️' + _('Upcoming'), callback_data='reservationsView_pending_confirmed')],
        [InlineKeyboardButton(text='⌛' + _('Past'), callback_data='reservationsView_completed_cancelled')],
        [InlineKeyboardButton(text=notif_text, callback_data='notifsToggle')],
        [InlineKeyboardButton(text='⫶☰ ' + _('Back to Main Menu'), callback_data='mainMenu')],
    ]
    )
    return back_button


async def view_booking_buttons(state_data: dict, *args):
    builder = InlineKeyboardBuilder()
    locale = state_data.get("locale", "en")
    for booking in args:
        date_format = datetime.fromisoformat(booking[3])
        start = ':'.join(booking[1].split(':')[:-1])
        end = ':'.join(booking[2].split(':')[:-1])
        builder.button(text= _('Reservation for') + f' {format_date(date_format, format="d MMM", locale=locale)}, '
                       + f'{start} - {end}', callback_data=f'bookingDetails_{booking[0]}')
        print(booking[1])
        builder.adjust(1)

    page_builder = InlineKeyboardBuilder()
    page_builder.button(text=_('Return to profile settings'), callback_data='profile')
    page_builder.adjust(1)
    return builder.attach(page_builder).as_markup()


async def booking_detail_buttons(state_data: dict):
    page_builder = InlineKeyboardBuilder()
    status1, status2 = state_data['statuses']
    if status1 == 'pending' and status2 == 'confirmed':
        page_builder.button(text='🗓️' + _('Return to upcoming reservations'), callback_data='reservationsView_pending_confirmed')
    elif status1 == 'completed' and status2 == 'cancelled':
        page_builder.button(text='⌛' + _('Return to past reservations'), callback_data='reservationsView_completed_cancelled')
    page_builder.adjust(1)
    return page_builder.as_markup()


