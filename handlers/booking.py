from datetime import datetime
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from babel.dates import format_date
from babel.numbers import format_currency

from BronTelegramBot.handlers.base import clear_state
from BronTelegramBot.keyboards.keyboard_base import back_to_main_menu_button
from BronTelegramBot.middlewares.database import *
from BronTelegramBot.middlewares.notification_middleware import NotificationMiddleware
from BronTelegramBot.states import BookingState, SearchParams
from BronTelegramBot.keyboards.keyboard_booking import *
from aiogram import html
from aiogram.utils.i18n import gettext as _
from BronTelegramBot.utils import text_to_datetime, datetime_to_text

booking_router = Router()
booking_router.message.middleware(NotificationMiddleware())


@booking_router.callback_query(lambda call: 'bookingMenu' in call.data)
async def booking_menu(call: CallbackQuery, state: FSMContext):
    await clear_state(call, state)
    await call.message.edit_text(_('Booking...'), reply_markup=await booking_menu_markup())


@booking_router.callback_query(lambda call: 'categoryChoose' in call.data)
async def booking_categories(call: CallbackQuery, state: FSMContext):
    cat_dict = await get_categories()
    await call.message.edit_text(_('Choose a category:'), reply_markup=await booking_category_buttons(**cat_dict))
    await state.set_state(SearchParams.category)


@booking_router.callback_query(lambda call: 'searchBusinessByCat' in call.data)
async def businesses_in_cat(call: CallbackQuery, state: FSMContext):
    comm, category = call.data.split('_')
    results = await search_businesses_by_category(category)
    amt = str(len(results))
    data = await state.update_data(category=category)
    cat_dict = await get_categories()
    await call.message.edit_text(
        _('{amt} Companies found in "{category}" category').format(
            amt=html.quote(amt), category=html.quote(cat_dict[category].capitalize())), reply_markup=await
        choose_business_menu(data, *results))


@booking_router.callback_query(lambda call: 'searchBooking' in call.data)
async def request_search_query(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(_('Enter your search query:'), reply_markup=await back_to_booking_menu())
    await state.set_state(SearchParams.query)


@booking_router.message(SearchParams.query)
async def businesses_by_query(message: Message, state: FSMContext):
    data = await state.update_data(query=message.text)
    results = await search_businesses_by_query(data['query'])
    amt = str(len(results))
    await state.update_data(res_count=amt)
    data = await state.update_data(search_results=results)

    if results:
        await message.answer(_('{amt} companies found for "{query}" ').format(
            query=html.quote(data['query']), amt=html.quote(amt)), reply_markup=await choose_business_menu(data, *results))
    else:
        await message.answer(_('No companies found for "{query}" ').format(
            query=html.quote(data['query']), amt=html.quote(amt)), reply_markup=await choose_business_menu(data))
    await state.set_state(BookingState.business_id)
    await state.set_state(BookingState.business_name)


@booking_router.callback_query(lambda call: 'repeatSearch' in call.data)
async def businesses_return_to_query(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    query = data['query']
    amt = data['res_count']
    results = data['search_results']

    if results:
        try:
            await call.message.edit_text(_('{amt} companies found for "{query}" ').format(
            query=html.quote(query), amt=html.quote(amt)), reply_markup=await choose_business_menu(data, *results))
        except:
            await call.message.answer(_('{amt} companies found for "{query}" ').format(
                query=html.quote(query), amt=html.quote(amt)), reply_markup=await choose_business_menu(data, *results))
    else:
        await call.message.edit_text(_('Booking...'), reply_markup=await booking_menu_markup())
    await state.set_state(BookingState.business_id)
    await state.set_state(BookingState.business_name)


@booking_router.callback_query(lambda call: 'chooseBusiness' in call.data)
async def choose_branch(call: CallbackQuery, state: FSMContext):
    comm, business_id = call.data.split('_')
    await state.update_data(business_id=business_id)
    business_name = await business_name_by_id(business_id)
    data = await state.update_data(business_name=business_name)
    results = await search_branches_by_business_id(business_id)
    amt = len(results)
    if data.get('category'):
        reply_markup = await branch_choices(data, *results)
    elif data.get('query'):
        reply_markup = await branch_choices(data, *results)
    else:
        reply_markup = await branch_choices(data, *results)
    await call.message.edit_text(_(
        '{business_name} has {amt} branches/subsidiaries:').format(
        business_name=html.quote(business_name), amt=html.quote(str(amt))),
        reply_markup=reply_markup)


@booking_router.callback_query(lambda call: 'chooseBranch' in call.data)
async def choose_service(call: CallbackQuery, state: FSMContext):
    comm, branch_id = call.data.split('_')
    data = await state.update_data(branch_id=branch_id)
    business_id = data['business_id']
    business_name = data['business_name']
    results = await search_services_by_business(business_id)
    amt = str(len(results))

    await call.message.edit_text(_('{business_name} offers {amt} service(s) for booking:').format(
        business_name=html.quote(business_name), amt=html.quote(amt)),
        reply_markup=await choose_business_service_menu(business_id, *results))


@booking_router.callback_query(lambda call: 'chooseService' in call.data)
async def choose_date(call: CallbackQuery, state: FSMContext):
    comm, service_id = call.data.split('_')
    service_title, service_duration, service_price = await service_title_duration_and_price_by_id(service_id)
    await state.update_data(service_title=service_title)
    await state.update_data(service_price=service_price)
    await state.update_data(service_id=service_id)
    data = await state.update_data(service_duration=service_duration)
    blocked_dates = [date[0] for date in await search_blocked_dates_by_business(business_id=data['business_id'])]
    print(blocked_dates, 'blocked_dates')

    working_hours = await search_working_hours_by_business_id(business_id=data['business_id'])
    await state.update_data(working_hours=working_hours)
    await state.update_data(blocked_dates=blocked_dates)
    await call.message.edit_text(_('Choose a date:'),
                                     reply_markup=await booking_date_buttons(data['branch_id'],
                                                                             data['locale'],
                                                                             page='1',
                                                                             blocked_dates=blocked_dates,
                                                                             working_hours=working_hours))




@booking_router.callback_query(lambda call: 'datePage' in call.data)
async def date_pagination(call: CallbackQuery, state: FSMContext):
    comm, page_num = call.data.split('_')
    data = await state.get_data()
    business_id = data['business_id']
    locale = data['locale']
    blocked_dates = data['blocked_dates']
    working_hours = data['working_hours']
    await call.message.edit_text(_('Choose a date:'), reply_markup=await booking_date_buttons(business_id,
                                                                                              locale=locale,
                                                                                              page=str(page_num),
                                                                                              blocked_dates=blocked_dates,
                                                                                              working_hours=working_hours))

async def choose_hour_helper(data: dict, page_num):
    service_duration = data['service_duration']
    date = data['booking_date']
    service_id = data['service_id']
    working_hours = data['working_hours']
    return date, service_id, service_duration, str(page_num), *working_hours


@booking_router.callback_query(lambda call: 'bookingDate' in call.data)
async def choose_hour(call: CallbackQuery, state: FSMContext):
    comm, date_unformatted = call.data.split('_')
    data = await state.update_data(booking_date=text_to_datetime(date_unformatted, "%Y-%m-%d"))
    service_title = data['service_title']
    info = await choose_hour_helper(data, 1)
    reply_markup = await choose_hours(*info)
    await call.message.edit_text(_(
        'The duration of your chosen service "{service_title}" is {service_duration} minutes.\nChoose the timeframe of your booking:'
    ).format(service_duration=html.quote(str(info[2])),
             service_title=html.quote(service_title)),
                                 reply_markup=reply_markup)


@booking_router.callback_query(lambda call: 'bookingTimePage' in call.data)
async def choose_hour_pagination(call: CallbackQuery, state: FSMContext):
    comm, page_num = call.data.split('_')
    data = await state.get_data()
    service_title = data['service_title']
    info = await choose_hour_helper(data, page_num)
    reply_markup = await choose_hours(*info)
    await call.message.edit_text(_(
        'The duration of your chosen service "{service_title}" is {service_duration} minutes.\nChoose the timeframe of your booking:'
    ).format(
        service_duration=html.quote(str(info[2])), service_title=html.quote(service_title)
    ), reply_markup=reply_markup)


@booking_router.callback_query(lambda call: 'startEndBookingTime' in call.data)
async def choose_booking_for_one(call: CallbackQuery, state: FSMContext):
    comm, start_time, end_time = call.data.split('_')
    start_formatted = text_to_datetime(start_time, '%H-%M-%S')
    end_formatted = text_to_datetime(end_time, '%H-%M-%S')
    await state.update_data(start_time=start_formatted)
    data = await state.update_data(end_time=end_formatted)
    date = data['booking_date']

    await call.message.edit_text(_('Choose which of the following options applies to your reservation/booking:'),
                                 reply_markup=await choose_alone_or_with_guests(date))


@booking_router.callback_query(lambda call: 'guestChoice' in call.data)
async def choose_number_of_guests(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    start_time, end_time = data['start_time'], data['end_time']
    reply_markup = await choose_number_of_guests_buttons(start=start_time, end=end_time, page='1')

    await call.message.edit_text(_('Choose the number of guests:'), reply_markup=reply_markup)


@booking_router.callback_query(lambda call: 'guestPage' in call.data)
async def guest_paginations(call: CallbackQuery, state: FSMContext):
    comm, page_num = call.data.split('_')
    data = await state.get_data()
    start_time, end_time = data['start_time'], data['end_time']

    await call.message.edit_text(_('Choose the number of guests:'), reply_markup=await choose_number_of_guests_buttons(
        start_time, end_time, str(page_num)))


async def product_message(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    products = await products_by_business_id(data['business_id'])

    if data.get('products_info'):
        products_info = data['products_info']
        products_chosen = len(products_info)
        price = sum([int(product[2]) for product in products_info])
        await call.message.edit_text(_('''Choose additional products alongside your reservation or skip this step:
    \nYou chose {product_qty} product(s), ({price})''').format(
            product_qty=html.quote(str(products_chosen)),
            price=html.quote(format_currency(price, "UZS", locale='uz_UZ'))),
            reply_markup=await choose_products_buttons(data, *products))
    else:
        await call.message.edit_text(_('Choose additional products alongside your reservation or skip this step:'),
                                     reply_markup=await choose_products_buttons(data, *products))

@booking_router.callback_query(lambda call: 'chooseNumOfGuests' in call.data)
async def choose_products(call: CallbackQuery, state: FSMContext):
    comm, guests = call.data.split('_')
    await state.update_data(guest_count=int(guests))
    await product_message(call, state)


@booking_router.callback_query(lambda call: 'chooseProduct' in call.data)
async def product_pagination(call: CallbackQuery, state: FSMContext):
    comm, product_id, action = call.data.split('_')
    data = await state.get_data()
    print(data)
    current_product_info = await products_info_by_ids(product_id)
    products_info = data.get('products_info')
    if products_info:
        if action == 'add':
            products_info.append(current_product_info)
        else:
            products_info.remove(current_product_info)
    else:
        products_info = [current_product_info]
    await state.update_data(products_info=products_info)
    await product_message(call, state)


@booking_router.callback_query(lambda call: 'productsProceed' in call.data)
async def leave_note(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    products_info = data['products_info']
    product_price = sum([int(product[2]) for product in products_info])
    if len(call.data.split('_')) == 2:
        products_info = []
        product_price = 0
    await state.update_data(products_info=products_info)
    await state.update_data(products_total_price=product_price)
    guest_count = data['guest_count']
    await call.message.edit_text(_("Leave an additional message (or click the skip button)"),
                                 reply_markup=await note_buttons(guest_count))
    await state.set_state(BookingState.note)


async def final_check_tasks(state: FSMContext):
    data = await state.get_data()
    service_price = data['service_price']
    num_of_guests = data['guest_count']
    if num_of_guests > 0:
        total_price = int(service_price) * num_of_guests
    else:
        total_price = int(service_price)
    if data.get('products_total_price'):
        total_price += int(data['products_total_price'])
    data = await state.update_data(total_price=total_price)
    final_text = await format_final_text(state_data=data)
    return final_text


@booking_router.message(BookingState.note)
async def final_check(message: Message, state: FSMContext):
    await state.update_data(note=message.text)
    final_text = await final_check_tasks(state=state)
    await message.answer(final_text, reply_markup=await final_button_confirm())


@booking_router.callback_query(lambda call: 'skipNoteStep' in call.data)
async def final_check_skipped(call: CallbackQuery, state: FSMContext):
    final_text = await final_check_tasks(state=state)
    await call.message.edit_text(final_text, reply_markup=await final_button_confirm())

# implement payment and confirmation dialogue after QR codes are implemented
@booking_router.callback_query(lambda call: 'bookingFinalConfirm' in call.data)
async def confirm_booking(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await call.message.edit_text(_('Payment services are still in development'), reply_markup=await back_to_main_menu_button())
    booking_data = await booking_args(data)
    booking_id = await create_booking(*booking_data)
    blocked_args = await blocked_date_args(data)
    await block_date(*blocked_args)
    if data.get('products_info'):
        for product in data['products_info']:
            await insert_booking_products(product[0], booking_id)
    await clear_state(call, state)


async def booking_args(state_data: dict):
    return int(state_data['user_id']), int(state_data['business_id']),\
           int(state_data['service_id']), int(state_data['branch_id']),\
           float(int(state_data['total_price'])), int(state_data.get('guest_count', 0)),\
           state_data['start_time'].time().isoformat(), state_data['end_time'].time().isoformat(),\
           state_data['booking_date'].date().isoformat(), state_data.get('note', ''),\
           'pending', '', datetime_now()


async def blocked_date_args(state_data: dict):
    return state_data['booking_date'].date().isoformat(), 'This date is booked', int(state_data['business_id']), datetime_now()


async def get_categories():
    options = {
        "gym": _("Gym"),
        "spa": _("Spa"),
        "salon": _("Salon"),
        "clinic": _("Clinic")}
    return options


async def format_final_text(state_data):
    localized_msg = _('''Your total price is {total_price}
Please make sure your booking details are correct:

Company name: {business_name}\nChosen service: {service_title}
Service duration: {service_duration} minutes\nBooked date: {booking_date}
Booked timeslot: {start_time} - {end_time}'''
                      ).format(
        total_price=html.quote(format_currency(state_data['total_price'], 'UZS', locale="uz_UZ")),
        business_name=html.quote(state_data['business_name']),
        service_title=html.quote(state_data['service_title']),
        service_duration=html.quote(str(state_data['service_duration'])),
        booking_date=html.quote(
            format_date(state_data['booking_date'],
                        format='EEEE, d MMMM', locale=state_data['locale'])).capitalize(),
        start_time=html.quote(datetime_to_text(state_data['start_time'], "%H:%M")),
        end_time=html.quote(datetime_to_text(state_data['end_time'], "%H:%M")))

    if state_data.get('products_info'):
        products_info = state_data['products_info']
        products_price = state_data['products_total_price']
        products_str = []
        for product in products_info:
            products_str.append(
                f'{product[1]} - {format_currency(product[2], "UZS", locale="uz_UZ")}')
            products_info.remove(product)
        products_text = ', '.join(products_str)

        localized_msg += _('\nAdditional products: {products_info}').format(
            products_info=html.quote(products_text))

        localized_msg += _(
            '\nPrice of products: {products_price}').format(
            products_price=html.quote(format_currency(products_price, 'UZS', locale="uz_UZ")))
    if state_data.get('note'):
        localized_msg += _(
            '\nAdditional note: {note}').format(note=html.quote(state_data['note']))
    if state_data.get('guest_count'):
        localized_msg += _(
            '\nGuests invited: {guest_count}').format(guest_count=html.quote(str(state_data['guest_count'])))
    return localized_msg
