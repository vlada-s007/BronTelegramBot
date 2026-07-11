import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from apscheduler.schedulers.asyncio import AsyncIOScheduler

WORKDIR = Path(__file__).parent.parent

scheduler = AsyncIOScheduler()

def timedelta_to_datetime(timedelta):
    start_sec = int(timedelta.total_seconds())
    start_min = (start_sec % 3600) // 60
    start_hour = start_sec // 3600
    datetime_val = datetime.time(hour=start_hour, minute=start_min)
    return datetime_val


def datetime_now():
    return datetime.datetime.now()


def text_to_datetime(text, format):
    return datetime.datetime.strptime(text, format)


def datetime_to_text(text, format):
    return datetime.datetime.strftime(text, format)


def simple_timedelta(minutes, *args):
    return datetime.timedelta(minutes=minutes, hours=args[0])


def combine_time(date, time):
    return datetime.datetime.combine(date, time)
