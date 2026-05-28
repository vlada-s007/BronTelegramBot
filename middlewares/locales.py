from aiogram.fsm.context import FSMContext
from aiogram.types import TelegramObject
from aiogram.utils.i18n import I18n
from aiogram.utils.i18n.middleware import FSMI18nMiddleware
from typing_extensions import Any

from bronTelegramBot.utils import WORKDIR

i18n = I18n(path=WORKDIR / 'bronTelegramBot' / 'locales', default_locale="en", domain="messages")
i18n_middleware = FSMI18nMiddleware(i18n=i18n)



