import datetime
from babel.dates import format_date
from babel.numbers import format_currency
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import html
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder
import cyrtranslit
import unicodedata

from BronTelegramBot.utils import timedelta_to_datetime, text_to_datetime


async def booking_menu_markup():
    builder = InlineKeyboardBuilder()
    builder.button(text=f'🗂️ ' + _('Choose Companies by Category'), callback_data='categoryChoose')
    builder.button(text=f'🔎 ' + _('Search Companies'), callback_data='searchBooking')
    builder.button(text=f'⫶☰ ' + _('Back to Main Menu'), callback_data='mainMenu')
    builder.adjust(1, 1, 1)
    return builder.as_markup()


async def back_to_booking_menu():
    page_buttons = InlineKeyboardBuilder()
    page_buttons.button(text=f'⬅️📋 ' + _('Return to Booking Menu'), callback_data='bookingMenu')
    return page_buttons.as_markup()


async def booking_category_buttons(**kwargs):
    builder = InlineKeyboardBuilder()
    for key, title in kwargs.items():
        print(key, title)
        builder.button(text=title, callback_data=f'searchBusinessByCat_{key}')
        builder.adjust(1)
    page_buttons = InlineKeyboardBuilder()
    page_buttons.button(text='⬅️📋 '+ _('Return to Booking Menu'), callback_data='bookingMenu')
    builder.attach(page_buttons)
    return builder.as_markup()


async def choose_business_menu(state: dict, *args):
    builder = InlineKeyboardBuilder()
    print(args, 'args')
    if args:
        for business in args:
            print(business, 'unpack')
            builder.button(text=business[1], callback_data=f'chooseBusiness_{business[0]}')
    page_buttons = InlineKeyboardBuilder()
    if state.get('category'):
        page_buttons.button(text='⬅️🗂️ ' + _('Return to category filtering'),
                            callback_data=f'categoryChoose_{state["category"]}')
    else:
        page_buttons.button(text='⬅️📋 ' + _('Return to Booking Menu'),
                            callback_data=f'bookingMenu')

    builder.attach(page_buttons)
    return builder.as_markup()

async def branch_choices(state: dict, *args):
    builder = InlineKeyboardBuilder()
    for branch in args:
        builder.button(text=f'{branch[1]} - {branch[2]}', callback_data=f'chooseBranch_{branch[0]}')
        builder.adjust(1)
    page_buttons = InlineKeyboardBuilder()
    if state.get('category'):
        page_buttons.button(text='⬅️🗂️ ' + _('Return to companies in "{category}" category').format(category=html.quote(state['category'].capitalize())),
                            callback_data=f'searchBusinessByCat_{state["category"]}')
    elif state.get('query') and len(state.get('res_count')) > 0:
        page_buttons.button(text='⬅️🔎 ' + _('Return to Search Results for "{query}"').format(query=html.quote(state['query'])),
                            callback_data=f'repeatSearch')
    else:
        page_buttons.button(text='⬅️📋 ' + _('Return to Booking Menu'),
                            callback_data=f'bookingMenu')
    return builder.attach(page_buttons).as_markup()


async def choose_business_service_menu(business_id, *args):
    builder = InlineKeyboardBuilder()
    for service in args:
        builder.button(text=service[1], callback_data=f'chooseService_{service[0]}')
        builder.adjust(1)
    page_buttons = InlineKeyboardBuilder()
    page_buttons.button(text=f'⬅️📍 ' + _('Return to choosing a branch/subsidiary'), callback_data=f'chooseBusiness_{business_id}')
    return builder.attach(page_buttons).as_markup()


async def booking_date_buttons(branch_id, locale, page, blocked_dates: list, working_hours: list):
    builder = InlineKeyboardBuilder()
    today = datetime.date.today()
    pages = {
        '1': [range(1, 8), 4, 2],
        '2': [range(8, 15), 1, 3],
        '3': [range(15, 22), 2, 4],
        '4': [range(22, 29), 3, 1]
    }
    for num_day in pages[page][0]:
        button_day = (today + datetime.timedelta(days=num_day))
        for week_day in working_hours:
            if week_day[0] == button_day.weekday() and week_day[1] == 0:
                if not blocked_dates or str(button_day) not in blocked_dates:
                    formatted = (format_date(button_day, format='EEE, d MMM', locale=locale)).capitalize()
                    builder.button(text=formatted, callback_data=f'bookingDate_{button_day.strftime("%Y-%m-%d")}')
                    builder.adjust(1)

    page_builder = InlineKeyboardBuilder()
    page_builder.button(text='◀️', callback_data=f'datePage_{pages[page][1]}')
    page_builder.button(text='▶️', callback_data=f'datePage_{pages[page][2]}')
    page_builder.button(text=f'⬅️🛎️ ' + _("Return to choosing services"), callback_data=f'chooseBranch_{branch_id}')
    page_builder.adjust(2, 1)
    builder.attach(page_builder)
    return builder.as_markup()


async def choose_hours(date, service_id, service_duration, page, *args):
    builder = InlineKeyboardBuilder()
    duration = datetime.timedelta(minutes=service_duration)

    pages = {
        '1': [range(0, 300, 30)]}
    for weekday in args:

        if date.weekday() == weekday[0] and weekday[1] == 0:
            print(type(weekday[2]))
            open_t, close_t = text_to_datetime(weekday[2], "%H:%M:%S"), text_to_datetime(weekday[3], "%H:%M:%S")
            open_timedelta = datetime.timedelta(hours=open_t.hour, minutes=open_t.minute)
            close_timedelta = datetime.timedelta(hours=close_t.hour, minutes=close_t.minute)
            diff = int((((close_timedelta - open_timedelta).total_seconds()) // 60)-60)

            if diff >= 300 and diff <= 600:
                pages['2'] = [range(300, diff, 30)]

                val = pages['1']
                pages['1'] = val + [2, 2]
                val2 = pages['2']
                pages['2'] = val2 + [1, 1]

            elif diff >= 600 and diff <= 900:
                pages['2'] = [range(300, 600, 30)]
                pages['3'] = [range(300, diff, 30)]

                val = pages['1']
                pages['1'] = val + [3, 2]
                val2 = pages['2']
                pages['2'] = val2 + [1, 3]
                val3 = pages['3']
                pages['3'] = val3 + [2, 1]



            for i in pages[page][0]:
                increment = datetime.timedelta(minutes=i)
                start_timedelta = open_timedelta + increment
                end_timedelta = start_timedelta + duration
                datetime_start = timedelta_to_datetime(start_timedelta)
                datetime_end = timedelta_to_datetime(end_timedelta)

                builder.button(text=f'{datetime_start.strftime("%H:%M")} - {datetime_end.strftime("%H:%M")}',
                               callback_data=
                               f'startEndBookingTime_{datetime_start.strftime("%H-%M-%S")}_{datetime_end.strftime("%H-%M-%S")}')
                builder.adjust(1)
            page_builder = InlineKeyboardBuilder()
            if diff > 300 and pages.get('2'):
                page_builder.button(text='◀️', callback_data=f'bookingTimePage_{pages[page][1]}')
                page_builder.button(text='▶️', callback_data=f'bookingTimePage_{pages[page][2]}')
                page_builder.button(text=f'⬅️ ' + _("Return to choosing a date of your reservation"), callback_data=f'chooseService_{service_id}')
                page_builder.adjust(2, 1)
            else:
                page_builder.button(text=f'⬅️ ' + _("Return to choosing a date of your reservation"), callback_data=f'chooseService_{service_id}')
            builder.attach(page_builder)
    return builder.as_markup()


async def choose_alone_or_with_guests(date):
    builder = InlineKeyboardBuilder()
    builder.button(text='👤' + _("I'm making a reservation for myself only"), callback_data='chooseNumOfGuests_0')
    builder.button(text='👥' + _("I'm coming with guests (proceed to choosing the amount of guests)"), callback_data='guestChoice')
    page_buttons = InlineKeyboardBuilder()
    page_buttons.button(text=f'⬅️🕔 ' + _('Return to choosing your booking/reservation timeframe'),
                        callback_data=f'bookingDate_{date.strftime("%Y-%m-%d")}')
    builder.adjust(1, 1, 1)
    return builder.attach(page_buttons).as_markup()


async def choose_number_of_guests_buttons(start, end, page):
    builder = InlineKeyboardBuilder()
    pages = {
        '1': [range(1, 11), 4, 2],
        '2': [range(11, 21), 1, 3],
        '3': [range(21, 31), 2, 4],
        '4': [range(31, 41), 3, 1]
    }
    for guest_num in pages[str(page)][0]:
        builder.button(text=f'{guest_num}', callback_data=f'chooseNumOfGuests_{guest_num}')
        builder.adjust(1)

    page_builder = InlineKeyboardBuilder()
    page_builder.button(text='◀️', callback_data=f'guestPage_{pages[str(page)][1]}')
    page_builder.button(text='▶️', callback_data=f'guestPage_{pages[str(page)][2]}')
    page_builder.button(text='❌👥 ' + _("I'm making a reservation for myself only"), callback_data='chooseNumOfGuests_0')
    page_builder.button(text='⬅️👤 ' + _('Return to choosing your booking/reservation type'), callback_data=f'startEndBookingTime_{start.strftime("%H-%M-%S")}_{end.strftime("%H-%M-%S")}')
    page_builder.adjust(2, 1, 1)
    builder.attach(page_builder)
    return builder.as_markup()


async def choose_products_buttons(state:dict, *args):
    builder = InlineKeyboardBuilder()
    for product in args:
        if state.get('products_info'):
            products_info = state['products_info']
            if product in products_info:
                builder.row(InlineKeyboardButton(text=f'✅ {product[1]} - {format_currency(product[2], "UZS", locale="uz_UZ")}',
                                                 callback_data=f'chooseProduct_{product[0]}_remove'))
            else:
                builder.row(InlineKeyboardButton(text=f'{product[1]} - {format_currency(product[2], "UZS", locale="uz_UZ")}',
                                                 callback_data=f'chooseProduct_{product[0]}_add'))
        else:
            builder.row(InlineKeyboardButton(text=f'{product[1]} - {format_currency(product[2], "UZS", locale="uz_UZ")}',
                                             callback_data=f'chooseProduct_{product[0]}_add'))
    page_buttons = InlineKeyboardBuilder()
    if state.get('products_info'):
        page_buttons.button(text='✅🛍️ ' + _('Proceed and order chosen product(s)'), callback_data='productsProceed')
        page_buttons.adjust(1)
    page_buttons.button(text='❌🛍️ ' + _('Skip this step (this will remove any chosen products)'),
                        callback_data='productsProceed_clear')
    guest_count = state.get('guest_count', 0)
    if guest_count > 0:
        page_buttons.button(text=f'⬅️👤 ' + _('Return choosing the number of guests'), callback_data=f'guestChoice')
    else:
        page_buttons.button(text='⬅️👤 ' + _('Return to choosing your booking/reservation type'), callback_data=f'startEndBookingTime_{state["start_time"].strftime("%H-%M-%S")}_{state["end_time"].strftime("%H-%M-%S")}')
    page_buttons.adjust(1, 1)
    return builder.attach(page_buttons).as_markup()

async def note_buttons(num_of_guests):
    builder = InlineKeyboardBuilder()
    builder.button(text='⏩ ' + _('Skip this step'), callback_data='skipNoteStep')
    builder.button(text=f'⬅️👤 ' + _('Return to choosing products'), callback_data=f'chooseNumOfGuests_{num_of_guests}')
    builder.adjust(1, 1)

    return builder.as_markup()

async def final_button_confirm():
    builder = InlineKeyboardBuilder()
    builder.button(text=f'✅💳 ' + _('Confirm and proceed to pay now'), callback_data='bookingFinalConfirm')
    builder.button(text=f'✅ ' + _('Confirm reservation/booking'), callback_data='bookingConfirmWithoutPayment')
    builder.button(text=f'❌ ' + _('Cancel reservation/booking and return to the main menu'), callback_data='bookingConfirmWithoutPayment_cancel')
    builder.adjust(1, 1, 1)
    return builder.as_markup()
