from aiogram.utils.i18n import I18n
from aiogram.utils.i18n.middleware import FSMI18nMiddleware
from bronTelegramBot.utils import WORKDIR

# pybabel extract --input-dirs=. -o locales/messages.pot
# pybabel update -i locales/messages.pot -d locales -D messages uz

i18n = I18n(path=WORKDIR / 'bronTelegramBot' / 'locales', default_locale="en", domain="messages")
i18n_middleware = FSMI18nMiddleware(i18n=i18n)



