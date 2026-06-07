from aiogram.fsm.state import StatesGroup, State


class UserState(StatesGroup):
    telegram_id = State()
    phone = State()
    first_name = State()
    last_name = State()
    user_database = State()
    user_language = State()
    user_password = State()
    user_only_phone = State()
    auth = State()


class LangState(StatesGroup):
    lang = State()


class TempMessageState(StatesGroup):
    message_id = State()



