from aiogram.fsm.state import StatesGroup, State


class UserState(StatesGroup):
    telegram_id = State()
    phone = State()
    user_database_id = State()
    auth = State()


class LangState(StatesGroup):
    lang = State()


class TempMessageState(StatesGroup):
    message_id = State()



