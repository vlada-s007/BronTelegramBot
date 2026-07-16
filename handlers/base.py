from aiogram import Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from typing import Union
from aiogram import html
from aiogram.utils.i18n import gettext as _
# from BronTelegramBot.middlewares.locales import i18n, i18n_middleware
from decouple import config
from aiogram.client.session.aiohttp import AiohttpSession
from BronTelegramBot.keyboards.keyboard_base import *
from BronTelegramBot.middlewares.database import search_bookings_for_profile, business_name_by_id, get_booking_details, \
    get_booking_products, products_by_business_id, products_info_by_ids
from BronTelegramBot.middlewares.locales import i18n_middleware

# for pythonanywhere
session = AiohttpSession(proxy="http://proxy.server:3128")
token = config('TOKEN')
bot = Bot(token=token, session=session)
from BronTelegramBot.middlewares.notifications import NotificationMiddleware

# token = config('TOKEN')
# bot = Bot(token)


base_router = Router()
base_router.message.middleware(NotificationMiddleware())


async def state_error_handling_or_clear(event: Union[Message, CallbackQuery],
                                        state: FSMContext, clear_request=False):
    data = await state.get_data()
    user_id = data.get('user_id')
    locale = data.get('locale')
    notifications = data.get('notifications', True)
    chat_id = data.get('chat_id', True)
    if not user_id and not locale and not notifications and not chat_id:
        try:
            await event.message.edit_text(_('An unexpected error occurred, please run the /start command again'),
                                    reply_markup=start_inline)
        except:
            await bot.send_message(chat_id=event.chat.id, text=_('An unexpected error occurred, please run the /start command again'),
                                    reply_markup=start_inline)
    else:
        if clear_request is True:
            await state.clear()
            await state.update_data(user_id=user_id)
            await state.update_data(locale=locale)
            await state.update_data(notifications=notifications)
            await state.update_data(chat_id=chat_id)
        elif clear_request is False:
            return True

@base_router.callback_query(lambda call: 'base_router_main_menu' in call.data)
async def get_main_menu(call:CallbackQuery, state: FSMContext):
    state = await state.get_data()
    print(state)
    try:
        await call.message.edit_text(_('Welcome to Bron. Choose your actions:'), reply_markup=await main_menu())
    except:
        await call.message.answer(_('Welcome to Bron. Choose your actions:'), reply_markup=await main_menu())


@base_router.callback_query(lambda call: 'chooseLocale' in call.data)
async def choose_language_menu(call: CallbackQuery):
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
    await call.message.edit_text(_('Contact us at @Bron_support'), reply_markup=await back_to_main_menu_button())


@base_router.callback_query(lambda call: 'about' in call.data)
async def about_command(call: CallbackQuery):
    await call.message.edit_text(_(
'''Welcome to Bron

Bron is an all-in-one platform that helps you discover trusted businesses, explore nearby services, and make reservations with ease.

Whether you're looking for a restaurant, café, beauty salon, clinic, hotel, or any other service, Bron helps you find reliable options near you. Browse verified businesses, compare ratings and reviews, explore products and services, and book in just a few taps.

With Bron, you can:

- Discover trusted businesses on an interactive map.
- Find nearby services based on your location.
- Browse products, services, photos, and business information.
- Read ratings and customer reviews.
- Make reservations quickly and securely.
- Save your favorite places and manage all your bookings in one account.
- Explore special offers and exclusive deals from businesses.

Our mission is to make finding trusted local businesses simple, convenient, and reliable, helping you save time and enjoy the best experiences.'''), \
reply_markup=await back_to_main_menu_button())


@base_router.callback_query(lambda call: 'profile' in call.data)
async def profile_command(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    notif_state = data['notifications']
    await call.message.edit_text(_('View your upcoming and past reservations or toggle your notification status'),
                                 reply_markup=await profile_view_buttons(notif_state))


@base_router.callback_query(lambda call: 'notifsToggle' in call.data)
async def change_notification_status(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    data = await state.update_data(notifications=not(data['notifications']))
    notif_state = data['notifications']
    await call.message.edit_text(_('View your upcoming and past reservations or toggle your notification status'),
                                 reply_markup=await profile_view_buttons(notif_state))


@base_router.callback_query(lambda call: 'reservationsView' in call.data)
async def reservations_view(call: CallbackQuery, state: FSMContext):
    comm, status1, status2 = call.data.split('_')
    data = await state.get_data()
    userexists = await state_error_handling_or_clear(call, state)
    if userexists is True:
        bookings = await search_bookings_for_profile(data['user_id'], status1, status2)
        if status1 == 'pending' and status2 == 'confirmed':
            booking_view_text = _('Your upcoming reservations:')
        elif status1 == 'completed' and status2 == 'cancelled':
            booking_view_text = _('Your past reservations:')
        await state.update_data(statuses=[status1, status2])
        await call.message.edit_text(booking_view_text, reply_markup=await view_booking_buttons(data, *bookings))


@base_router.callback_query(lambda call: 'bookingDetails' in call.data)
async def view_booking_details(call: CallbackQuery, state: FSMContext):
    comm, booking_id = call.data.split('_')
    res_list = await get_booking_details(booking_id)
    data = await state.get_data()
    print(data)
    await call.message.edit_text(text=await format_booking_details(booking_id, data, *res_list),
                                 reply_markup=await booking_detail_buttons(data))
    await state_error_handling_or_clear(call, state, True)


@base_router.callback_query(lambda call: 'mainMenu' in call.data)
async def back_to_main_menu(call: CallbackQuery, state: FSMContext):
    try:
        comm, comm2 = call.data.split('_')
        if comm2 == 'cancel':
            await state_error_handling_or_clear(call, state)
    except:
        pass
    await call.message.edit_text(_('Choose your actions:'), reply_markup=await main_menu())


async def get_statuses():
    options = {
        "pending": _("Pending"),
        "completed": _("Completed"),
        "confirmed": _("Confirmed"),
        "cancelled": _("Cancelled")}
    return options


async def format_booking_details(booking_id, state_data, *args):
    statuses = await get_statuses()
    status = statuses.get(args[-1])
    business_name = await business_name_by_id(args[1])
    service_id = args[2]
    service_info = await service_title_duration_and_price_by_id(service_id)
    total_price = format_currency(args[4], 'UZS', locale="uz_UZ")
    start = ':'.join(args[6].split(':')[:-1])
    end = ':'.join(args[7].split(':')[:-1])
    date_format = format_date(datetime.fromisoformat(args[8]), format="d MMM", locale=state_data["locale"])
    products = await get_booking_products(booking_id)

    localized_msg = _('''Booking status: {status}
The total price of this reservation is {total_price}

Company name: {business_name}\nChosen service: {service_title}
Service duration: {service_duration} minutes\nBooked date: {booking_date}
Booked timeslot: {start_time} - {end_time}'''
                      ).format(
        status=html.quote(status),
        total_price=html.quote(total_price),
        business_name=html.quote(business_name),
        service_title=html.quote(service_info[0]),
        service_duration=html.quote(str(service_info[1])),
        booking_date=html.quote(date_format),
        start_time=html.quote(start),
        end_time=html.quote(end))

    if products:
        products_info = [await products_info_by_ids(product_id[0]) for product_id in products]
        products_price = sum([int(product[2]) for product in products_info])
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
    if args[9] != '' and args[9] is not None:
        localized_msg += _(
            '\nAdditional note: {note}').format(note=html.quote(args[9]))
    if args[5] != 0:
        localized_msg += _(
            '\nGuests invited: {guest_count}').format(guest_count=html.quote(str(args[5])))
    return localized_msg

