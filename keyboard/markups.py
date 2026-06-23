import datetime
from babel.dates import format_date
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.i18n import lazy_gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder
import cyrtranslit
import unicodedata

from bronTelegramBot.utils import text_to_datetime, timedelta_to_datetime

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
    markup = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=text, callback_data='base_router_main_menu')]])
    return markup


async def main_menu(*args):
    builder = InlineKeyboardBuilder()
    builder.button(text=f'📋 {args[0]}', callback_data='bookingMenu')
    builder.button(text=f'👤 {args[1]}', callback_data='profile')
    builder.button(text=f'🌐 {args[2]}', callback_data='chooseLocale')
    builder.button(text=f'ℹ️ {args[3]}', callback_data='about')
    builder.button(text=f'🆘 {args[4]}', callback_data='help'),
    builder.adjust(1, 1, 1, 1, 1)
    return builder.as_markup()

async def back_to_main_menu_button(text):
    back_button = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f'⫶☰ {text}', callback_data='mainMenu')]]
    )
    return back_button


async def booking_menu_markup(*args):
    builder = InlineKeyboardBuilder()
    builder.button(text=f'🗂️ {args[0]}', callback_data='categoryChoose')
    builder.button(text=f'🔎 {args[1]}', callback_data='searchBooking')
    builder.button(text=f'⫶☰ {args[2]}', callback_data='mainMenu')
    builder.adjust(1, 1, 1)
    return builder.as_markup()


async def back_to_booking_menu(text):
    page_buttons = InlineKeyboardBuilder()
    page_buttons.button(text=f'⬅️📋 {text}', callback_data='bookingMenu')
    return page_buttons.as_markup()


async def booking_category_buttons(text, **kwargs):
    builder = InlineKeyboardBuilder()
    for key, title in kwargs.items():
        print(key, title)
        builder.button(text=title, callback_data=f'searchBusinessByCat_{key}')
        builder.adjust(1)
    page_buttons = InlineKeyboardBuilder()
    page_buttons.button(text=f'⬅️📋 {text}', callback_data='bookingMenu')
    builder.attach(page_buttons)
    return builder.as_markup()


async def choose_business_menu(text, state: dict, *args):
    builder = InlineKeyboardBuilder()
    print(args, 'args')
    if args:
        for business in args:
            print(business, 'unpack')
            builder.button(text=business[1], callback_data=f'chooseBusiness_{business[0]}')
    page_buttons = InlineKeyboardBuilder()
    if state.get('category'):
        page_buttons.button(text=f'⬅️🗂️ {text}', callback_data=f'categoryChoose')
    elif state.get('query') and args:
        page_buttons.button(text=f'⬅️🔎 {text}', callback_data=f'searchBooking')
    else:
        page_buttons.button(text=f'⬅️📋 {text}', callback_data=f'bookingMenu')
    builder.attach(page_buttons)
    return builder.as_markup()

async def branch_choices(text, state: dict, *args):
    builder = InlineKeyboardBuilder()
    for branch in args:
        builder.button(text=f'{branch[1]} - {branch[2]}', callback_data=f'chooseBranch_{branch[0]}')
    page_buttons = InlineKeyboardBuilder()
    if state.get('category'):
        page_buttons.button(text=f'⬅️🗂️ {text}', callback_data=f'searchBusinessByCat_{state["category"]}')
    elif state.get('query'):
        page_buttons.button(text=f'⬅️🔎 {text}', callback_data=f'repeatSearch')
    else:
        page_buttons.button(text=f'⬅️📋 {text}', callback_data=f'bookingMenu')
    return builder.attach(page_buttons).as_markup()

async def choose_business_service_menu(return_text, business_id, *args):
    builder = InlineKeyboardBuilder()
    for service in args:
        builder.button(text=service[1], callback_data=f'chooseService_{service[0]}')
        builder.adjust(1)
    page_buttons = InlineKeyboardBuilder()
    page_buttons.button(text=f'⬅️📍 {return_text}', callback_data=f'chooseBusiness_{business_id}')
    return builder.attach(page_buttons).as_markup()


async def booking_date_buttons(branch_id, return_text, locale, page, blocked_dates: list, working_hours: list):
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
                if not blocked_dates or button_day not in blocked_dates:
                    formatted = (format_date(button_day, format='EEEE, d MMMM', locale=locale)).capitalize()
                    builder.button(text=formatted, callback_data=f'bookingDate_{button_day.strftime("%Y-%m-%d")}')
                    builder.adjust(1)

    page_builder = InlineKeyboardBuilder()
    page_builder.button(text='◀️', callback_data=f'datePage_{pages[page][1]}')
    page_builder.button(text='▶️', callback_data=f'datePage_{pages[page][2]}')
    page_builder.button(text=f'⬅️🛎️ {return_text}', callback_data=f'chooseBranch_{branch_id}')
    page_builder.adjust(2, 1)
    builder.attach(page_builder)
    return builder.as_markup()


async def choose_hours(date, service_id, return_text, service_duration, page, *args):
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
                page_builder.button(text=f'⬅️ {return_text}', callback_data=f'chooseService_{service_id}')
                page_builder.adjust(2, 1)
            else:
                page_builder.button(text=f'⬅️ {return_text}', callback_data=f'chooseService_{service_id}')
            builder.attach(page_builder)
    return builder.as_markup()

async def choose_staff(return_text, date, *args):
    builder = InlineKeyboardBuilder()
    for staff in args:
        builder.button(text=f'{staff[1]} - {staff[2]}', callback_data=f'chooseStaff_{staff[0]}')
        builder.adjust(1)
    page_buttons = InlineKeyboardBuilder()
    page_buttons.button(text=f'⬅️🕔 {return_text}', callback_data=f'bookingDate_{date.strftime("%Y-%m-%d")}')
    return builder.attach(page_buttons).as_markup()


async def choose_number_of_guests_buttons(text, start, end, page):
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
    page_builder.button(text=f'⬅️👤 {text}', callback_data=f'startEndBookingTime_{start.strftime("%H-%M-%S")}_{end.strftime("%H-%M-%S")}')
    page_builder.adjust(2, 1)
    builder.attach(page_builder)
    return builder.as_markup()

async def note_buttons(text_skip, text_back, staff_id):
    builder = InlineKeyboardBuilder()
    builder.button(text=f'⏩ {text_skip}', callback_data='skipNoteStep')
    builder.button(text=f'⬅️👤 {text_back}', callback_data=f'chooseStaff_{staff_id}')
    builder.adjust(1, 1)
    return builder.as_markup()

async def final_button_confirm(text_confirm, text_deny):
    builder = InlineKeyboardBuilder()
    builder.button(text=f'✅ {text_confirm}', callback_data='bookingFinalConfirm')
    builder.button(text=f'❌ {text_deny}', callback_data='mainMenu')
    builder.adjust(1,1)
    return builder.as_markup()


