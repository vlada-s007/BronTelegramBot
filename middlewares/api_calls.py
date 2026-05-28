from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession, FormData
from decouple import config
from aiohttp import web

token = config('TOKEN')
bot = Bot(token)