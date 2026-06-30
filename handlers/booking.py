# Booking будет реализована после оформления API на авторизацию, это базовый тест
from datetime import datetime

from aiogram import Router
from aiogram.fsm.context import FSMContext

from aiogram.types import CallbackQuery, Message
from babel.dates import format_date

from bronTelegramBot.middlewares.database import search_businesses_by_category, search_businesses_by_query, \
    search_services_by_business, business_name_by_id, search_blocked_dates_by_business, \
    search_working_hours_by_business_id, \
    search_branches_by_business_id, service_title_duration_and_price_by_id, search_staff_by_business_id, \
    get_staff_name_and_position_by_staff_id
from bronTelegramBot.states import BookingState, SearchParams
from bronTelegramBot.keyboards.keyboard_booking import booking_menu_markup, booking_category_buttons, choose_business_menu, \
    choose_business_service_menu, booking_date_buttons, choose_hours, back_to_booking_menu, branch_choices, choose_number_of_guests_buttons, note_buttons, final_button_confirm

from aiogram import html
from aiogram.utils.i18n import gettext as _

from bronTelegramBot.utils import text_to_datetime, datetime_to_text

booking_router = Router()


@booking_router.callback_query(lambda call: 'bookingMenu' in call.data)
async def booking_menu(call: CallbackQuery):
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
        choose_business_menu(await back_to_booking_menu_text_if_query_or_cat(category=category), data, *results))
    print('edited')


@booking_router.callback_query(lambda call: 'searchBooking' in call.data)
async def request_search_query(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(_('Enter your search query:'), reply_markup=await back_to_booking_menu(
        await back_to_booking_menu_text()))
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
                query=html.quote(query), amt=html.quote(amt)), reply_markup=await choose_business_menu(
                await back_to_booking_menu_text_if_query_or_cat(query=query),
                data, *results))
    else:
        category = _('Choose Services By Category')
        search = _('Search Services and Products')
        back = _('Back to main menu')
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
        reply_markup=await choose_business_service_menu(
            await back_to_choosing_branch(), business_id, *results))


@booking_router.callback_query(lambda call: 'chooseService' in call.data)
async def choose_date(call: CallbackQuery, state: FSMContext):
    comm, service_id = call.data.split('_')
    service_title, service_duration, service_price = await service_title_duration_and_price_by_id(service_id)
    await state.update_data(service_title=service_title)
    await state.update_data(service_price=service_price)
    await state.update_data(service_id=service_id)
    data = await state.update_data(service_duration=service_duration)
    print(data)
    blocked_dates = await search_blocked_dates_by_business(business_id=data['business_id'])
    working_hours = await search_working_hours_by_business_id(business_id=data['business_id'])
    await state.update_data(working_hours=working_hours)
    await state.update_data(blocked_dates=blocked_dates)
    await call.message.edit_text(_('Choose a date:'),
                                     reply_markup=await booking_date_buttons(data['branch_id'],
                                                                             await get_return_text_business_choice(),
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
    await call.message.edit_text(_('Choose a date:'),
                                     reply_markup=await booking_date_buttons(business_id,
                                                                             await get_return_text_business_choice(),
                                                                             locale=locale,
                                                                             page=str(page_num),
                                                                             blocked_dates=blocked_dates,
                                                                             working_hours=working_hours))



@booking_router.callback_query(lambda call: 'bookingDate' in call.data)
async def choose_hour(call: CallbackQuery, state: FSMContext):
    comm, date_unformatted = call.data.split('_')
    data = await state.update_data(booking_date=text_to_datetime(date_unformatted, "%Y-%m-%d"))
    service_duration = data['service_duration']
    service_title = data['service_title']
    date = data['booking_date']
    service_id = data['service_id']
    working_hours = data['working_hours']
    return_text = await get_return_text_service_choice()
    reply_markup = await choose_hours(date, service_id, return_text, service_duration, '1', *working_hours)
    await call.message.edit_text(_(
        'The duration of your chosen service "{service_title}" is {service_duration} minutes.\nChoose the timeframe of your booking:'
    ).format(service_duration=html.quote(str(service_duration)),
             service_title=html.quote(service_title)),
                                 reply_markup=reply_markup)


@booking_router.callback_query(lambda call: 'bookingTimePage' in call.data)
async def choose_hour_pagination(call: CallbackQuery, state: FSMContext):
    comm, page_num = call.data.split('_')
    data = await state.get_data()
    service_duration = data['service_duration']
    service_title = data['service_title']
    date = data['booking_date']
    service_id = data['service_id']
    working_hours = data['working_hours']
    return_text = await get_return_text_service_choice()
    reply_markup = await choose_hours(date, service_id, return_text, service_duration, str(page_num), *working_hours)
    await call.message.edit_text(_(
        'The duration of your chosen service "{service_title}" is {service_duration} minutes:'
    ).format(
        service_duration=html.quote(str(service_duration)), service_title=html.quote(service_title)
    ), reply_markup=reply_markup)


# @booking_router.callback_query(lambda call: 'startEndBookingTime' in call.data)
# async def choose_staff_function(call: CallbackQuery, state: FSMContext):
#     comm, start_time, end_time = call.data.split('_')
#     start_formatted = text_to_datetime(start_time, '%H-%M-%S')
#     end_formatted = text_to_datetime(end_time, '%H-%M-%S')
#     await state.update_data(start_time=start_formatted)
#     data = await state.update_data(end_time=end_formatted)
#     date = data['booking_date']
#     business_id = data['business_id']
#     results = await search_staff_by_business_id(business_id)
#     amt = str(len(results))
#
#     await call.message.edit_text(_('{amt} staff members are available:').format(
#          amt=html.quote(amt)),
#         reply_markup=await choose_staff(
#             await back_to_hours_menu_text(), date, *results))

@booking_router.callback_query(lambda call: 'startEndBookingTime' in call.data)
async def choose_booking_for_one(call: CallbackQuery, state: FSMContext):
    comm, start_time, end_time = call.data.split('_')
    start_formatted = text_to_datetime(start_time, '%H-%M-%S')
    end_formatted = text_to_datetime(end_time, '%H-%M-%S')
    await state.update_data(start_time=start_formatted)
    data = await state.update_data(end_time=end_formatted)
    #     date = data['booking_date']
    #     business_id = data['business_id']


@booking_router.callback_query(lambda call: 'chooseStaff' in call.data)
async def choose_number_of_guests(call: CallbackQuery, state: FSMContext):
    comm, staff_id = call.data.split('_')
    staff_full_name, staff_position = await get_staff_name_and_position_by_staff_id(staff_id)
    await state.update_data(staff_full_name_and_position=f'{staff_full_name} - {staff_position}')
    data = await state.update_data(staff_id=staff_id)
    start_time, end_time = data['start_time'], data['end_time']
    reply_markup = await choose_number_of_guests_buttons(text=await back_to_staff_menu_text(), start=start_time, end=end_time, page='1')

    await call.message.edit_text(_('Choose the number of guests:'), reply_markup=reply_markup)


@booking_router.callback_query(lambda call: 'guestPage' in call.data)
async def guest_paginations(call: CallbackQuery, state: FSMContext):
    comm, page_num = call.data.split('_')
    data = await state.get_data()
    start_time, end_time = data['start_time'], data['end_time']

    await call.message.edit_text(_('Choose the number of guests:'), reply_markup=await choose_number_of_guests_buttons(
        await back_to_staff_menu_text(), start_time, end_time, str(page_num)))


@booking_router.callback_query(lambda call: 'chooseNumOfGuests' in call.data)
async def leave_note(call: CallbackQuery, state: FSMContext):
    comm, guests = call.data.split('_')
    data = await state.update_data(guest_count=guests)
    staff_id = data['staff_id']
    await call.message.edit_text(_("Leave an additional message (or click the skip button)"), reply_markup=await note_buttons(
        await skip_text(), await back_to_guest_menu_text(), staff_id))
    await state.set_state(BookingState.note)

@booking_router.message(BookingState.note)
async def final_check(message: Message, state: FSMContext):
    await state.update_data(note=message.text)
    data = await state.get_data()
    service_price = data['service_price']
    num_of_guests = data['guest_count']
    total_price = int(service_price) * int(num_of_guests)
    data = await state.update_data(total_price=total_price)
    final_text = await format_final_text(state_data=data)
    await message.answer(final_text,
                            reply_markup=await final_button_confirm(await confirm_text(), await cancel_text()))


@booking_router.callback_query(lambda call: 'skipNoteStep' in call.data)
async def final_check_skipped(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    service_price = data['service_price']
    num_of_guests = data['guest_count']
    total_price = int(service_price) * int(num_of_guests)
    data = await state.update_data(total_price=total_price)
    final_text = await format_final_text(state_data=data)
    await call.message.edit_text(final_text,
                                 reply_markup=await final_button_confirm(await confirm_text(), await cancel_text()))


# implement payment and after confirmation
# @booking_router.callback_query(lambda call: 'skipNoteStep' in call.data)
# async def confirm_booking(call: CallbackQuery, state: FSMContext):


async def get_return_text_business_choice():
    text = _("Return to choosing services")
    return text


async def get_return_text_service_choice():
    text = _("Return to choosing a date of your reservation")
    return text


async def get_categories():
    options = {
        "gym": _("Gym"),
        "spa": _("Spa"),
        "salon": _("Salon"),
        "clinic": _("Clinic")}
    return options



async def back_to_booking_menu_text_if_query_or_cat(**kwargs):
    if kwargs.get('category'):
        text = _('Return to category filtering')
    elif kwargs.get('query'):
        text = _('Return to Booking Menu')
    else:
        text = _('Return to Booking Menu')
    return text


async def back_to_booking_menu_text_filtered(**kwargs):
    if kwargs.get('category'):
        text = _('Return to companies in "{category}" category').format(category=html.quote(kwargs['category'].capitalize()))
    elif kwargs.get('query'):
        text = _('Return to Search Results for "{query}"').format(query=html.quote(kwargs['query']))
    else:
        text = _('Return to Booking Menu')
    return text


async def back_to_choosing_branch():
    text = _('Return to choosing branch')
    return text


async def confirm_text():
    text = _('Confirm reservation/booking')
    return text

async def cancel_text():
    text = _('Cancel reservation/booking and return to the main menu')
    return text



async def format_final_text(state_data):
    localized_msg = _('''Your total price is {total_price}
Please make sure your booking details are correct:
    
Company name: {business_name}\nChosen service: {service_title}
Service duration: {service_duration} minutes\nChosen staff: {staff_full_name_and_position}
Number of guests invited: {guest_count}\nBooked date: {booking_date}
Booked timeslot: {start_time} - {end_time}'''
                      ).format(
        total_price=html.quote(str(state_data['total_price'])),
        business_name=html.quote(state_data['business_name']),
        service_title=html.quote(state_data['service_title']),
        service_duration=html.quote(str(state_data['service_duration'])),
        staff_full_name_and_position=html.quote(state_data['staff_full_name_and_position']),
        guest_count=html.quote(str(state_data['guest_count'])),
        booking_date=html.quote(format_date(state_data['booking_date'], format='EEEE, d MMMM', locale=state_data['locale'])).capitalize(),
        start_time=html.quote(datetime_to_text(state_data['start_time'], "%H:%M")),
        end_time=html.quote(datetime_to_text(state_data['end_time'], "%H:%M")))

    if state_data.get('note'):
        localized_msg += _('\nAdditional note: {note}').format(note=html.quote(state_data['note']))
    return localized_msg
