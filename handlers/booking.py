# Booking будет реализована после оформления API на авторизацию, это базовый тест

from aiogram import Router
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _
from bronTelegramBot.keyboard.markups import booking_menu_markup

booking_router = Router()

class BookingState(StatesGroup):
    telegram_id = State()
    phone = State()
    access_token = State()
    refresh_token = State()

# Позже добавить middleware, которая будет посылать запрос на авторизацию
@booking_router.callback_query(lambda call: 'bookingMenu' in call.data)
async def booking_menu(call: CallbackQuery):
    category = _('Choose Services By Category')
    search = _('Search Services and Products')
    print(category, search)
    await call.message.edit_text(_('Booking...'), reply_markup=await booking_menu_markup(category, search))




# @booking_router.callback_query(lambda call: 'categoryChoose' in call.data):
# async def booking_categories(call: CallbackQuery, state: FSMContext):


