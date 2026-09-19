import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from apscheduler.schedulers.asyncio import AsyncIOScheduler

WORKDIR = Path(__file__).parent.parent

# Django stores DateTimeField as `timestamp with time zone` on Postgres.
# asyncpg does not silently reinterpret naive datetimes, so everything
# written to or compared against the database is made aware here.
LOCAL_TZ = ZoneInfo('Asia/Tashkent')

scheduler = AsyncIOScheduler(timezone=LOCAL_TZ)


def timedelta_to_datetime(timedelta):
    start_sec = int(timedelta.total_seconds())
    start_min = (start_sec % 3600) // 60
    start_hour = start_sec // 3600
    datetime_val = datetime.time(hour=start_hour, minute=start_min)
    return datetime_val


def datetime_now():
    """Timezone-aware 'now'.

    Was datetime.datetime.now() (naive).  Postgres timestamptz columns
    need an aware value, and comparing naive against aware raises
    TypeError.
    """
    return datetime.datetime.now(LOCAL_TZ)


def text_to_datetime(text, format):
    return datetime.datetime.strptime(text, format)


def datetime_to_text(text, format):
    return datetime.datetime.strftime(text, format)


def simple_timedelta(minutes, *args):
    return datetime.timedelta(minutes=minutes, hours=args[0])


def combine_time(date, time):
    """Combine a date and a time into an aware datetime."""
    return datetime.datetime.combine(date, time, tzinfo=LOCAL_TZ)


def time_to_timedelta(value):
    """datetime.time -> datetime.timedelta.

    Postgres `time` columns come back as datetime.time objects, where
    SQLite handed back 'HH:MM:SS' strings that the code used to parse
    with text_to_datetime().
    """
    return datetime.timedelta(hours=value.hour, minutes=value.minute,
                              seconds=value.second)


def hhmm(value):
    """Render a datetime.time (or datetime) as 'HH:MM'.

    Replaces the old ':'.join(value.split(':')[:-1]) trick that trimmed
    seconds off the strings SQLite returned.
    """
    return value.strftime('%H:%M')
