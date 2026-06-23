from aiogram.fsm.state import StatesGroup, State


class UserState(StatesGroup):
    telegram_id = State()
    phone = State()
    user_id = State()


class LangState(StatesGroup):
    lang = State()


class TempMessageState(StatesGroup):
    message_id = State()


class BookingState(StatesGroup):
    user_id = State()
    business_id = State()
    branch_id = State()
    business_name = State()
    service_id = State()
    service_title = State()
    service_duration = State()
    service_price = State()
    staff_id = State()
    staff_full_name_and_position = State()
    total_price = State()
    guest_count = State()
    start_time = State()
    end_time = State()
    booking_date = State()
    working_hours = State()
    blocked_dates = State()
    note = State()

class SearchParams(StatesGroup):
    category = State()
    query = State()
    search_results = State()
    cat_results = State()
    res_count = State()