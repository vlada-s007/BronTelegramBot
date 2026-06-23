import datetime
from pathlib import Path

WORKDIR = Path(__file__).parent.parent


def timedelta_to_datetime(timedelta):
    start_sec = int(timedelta.total_seconds())
    start_min = (start_sec % 3600) // 60
    start_hour = start_sec // 3600
    datetime_val = datetime.time(hour=start_hour, minute=start_min)
    return datetime_val


def text_to_datetime(text, format):
    return datetime.datetime.strptime(text, format)


def datetime_to_text(text, format):
    return datetime.datetime.strftime(text, format)


def simple_timedelta(minutes, *args):
    return datetime.timedelta(minutes=minutes, hours=args[0])


