from datetime import datetime
from aiogram import Router, F
from aiogram.client.bot import Bot
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, LabeledPrice, PreCheckoutQuery, ContentType
from babel.dates import format_date
from babel.numbers import format_currency
from typing import Union
from BronTelegramBot.handlers.base import state_error_handling_or_clear
from BronTelegramBot.keyboards.keyboard_base import back_to_main_menu_button, start_inline
from BronTelegramBot.middlewares.database import *
from BronTelegramBot.middlewares.notifications import NotificationMiddleware
from BronTelegramBot.states import BookingState, SearchParams
from BronTelegramBot.keyboards.keyboard_booking import *
from aiogram import html
from aiogram.utils.i18n import gettext as _
from BronTelegramBot.utils import text_to_datetime, datetime_to_text

# for pythonanywhere
from BronTelegramBot.handlers.booking import booking_error_handler

session = AiohttpSession(proxy="http://proxy.server:3128")
token = config('TOKEN')
payment = config('PAYMENT')
bot = Bot(token=token, session=session)

# token = config('TOKEN')
# payment = config('PAYMENT')
# bot = Bot(token)

payment_router = Router()
payment_router.message.middleware(NotificationMiddleware())


@payment_router.callback_query(lambda call: 'bookingFinalConfirm' in call.data)
async def confirm_booking(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    userexists = await state_error_handling_or_clear(call, state)
    if userexists is True:
        valueexists = await booking_error_handler(call,
                                                  state,
                                                  'user_id','business_id', 'service_id',
                                                  'branch_id','total_price', 'start_time',
                                                  'end_time', 'booking_date')
        if valueexists:
            await bot.send_invoice(chat_id=call.message.chat.id,
                                   title=_('Your booking:'),
                                   payload='bot-defined invoice payload',
                                   provider_token=payment,
                                   description=_('Pay with Click:'),
                                   currency='UZS',
                                   prices=[
                                       LabeledPrice(label='Total price', amount=int(data.get('total_price') * 100)),
                                   ],
                                   start_parameter='start_parameter')



@payment_router.pre_checkout_query(lambda query: True)
async def pre_checkout_query(pre_checkout_q: PreCheckoutQuery):
    await pre_checkout_q.answer(ok=True)

async def save_booking_to_db(booking_state, message: Message, state: FSMContext):
    data = await state.get_data()
    booking_data = await booking_args(booking_state, data)
    booking_id = await create_booking(*booking_data)
    blocked_args = await blocked_date_args(data)
    await block_date(*blocked_args)
    if data.get('products_info'):
        for product in data['products_info']:
            await insert_booking_products(product[0], booking_id)
    user_id = data.get('user_id')
    locale = data.get('locale')
    notifications = data.get('notifications', True)
    chat_id = data.get('chat_id', True)
    if not user_id and not locale and not notifications and not chat_id:
        await bot.send_message(chat_id=message.chat_id,
                               text=_('An unexpected error occurred, please run the /start command again'),
                               reply_markup=start_inline)
    else:
        await state.clear()
        await state.update_data(user_id=user_id)
        await state.update_data(locale=locale)
        await state.update_data(notifications=notifications)
        await state.update_data(chat_id=chat_id)

@payment_router.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: Message, state: FSMContext):
    await message.answer(text=_('Payment successful'), reply_markup=await back_to_main_menu_button())
    await save_booking_to_db('confirmed', message, state)

@payment_router.callback_query(lambda call: 'bookingConfirmWithoutPayment' in call.data)
async def confirm_booking(call: CallbackQuery, state: FSMContext):
    await call.message.answer(text=_('Your booking was saved successfully'), reply_markup=await back_to_main_menu_button())
    await save_booking_to_db('pending', call.message, state)


@payment_router.message(F.content_type == ContentType.REFUNDED_PAYMENT)
async def failed_payment(message: Message):
    await message.answer(text=_('Payment failed'), reply_markup=await back_to_main_menu_button())

@payment_router.callback_query(lambda call:'pendingReservationPayment' in call.data)
async def pay_existing_booking(call: CallbackQuery):
    comm, booking_price = call.data.split('_')
    booking_price = int(booking_price)
    await bot.send_invoice(chat_id=call.message.chat.id,
                           title=_('Your booking:'),
                           payload='bot-defined invoice payload',
                           provider_token=payment,
                           description=_('Pay with Click:'),
                           currency='UZS',
                           prices=[
                               LabeledPrice(label='Total price', amount=booking_price * 100),
                           ],
                           start_parameter='start_parameter')


async def booking_args(status, state_data: dict):
    return int(state_data['user_id']), int(state_data['business_id']),\
           int(state_data['service_id']), int(state_data['branch_id']),\
           float(int(state_data['total_price'])), int(state_data.get('guest_count', 0)),\
           state_data['start_time'].time().isoformat(), state_data['end_time'].time().isoformat(),\
           state_data['booking_date'].date().isoformat(), state_data.get('note', ''), \
           {status}, '', datetime_now()


async def blocked_date_args(state_data: dict):
    return state_data['booking_date'].date().isoformat(), 'This date is booked', int(state_data['business_id']), datetime_now()

