from babel.dates import format_date
import datetime
today = datetime.date.today()
fourweeks = today + datetime.timedelta(weeks=4)
print(f'4 weeks {fourweeks}')

# for num_day in range(1, 8):
#     button_day = (today + datetime.timedelta(days=num_day))
#     formatted = (format_date(button_day, format='EEEE, d MMMM', locale='ru')).capitalize()
#     print(formatted)
#     print(button_day.weekday())
# print()
# today = datetime.date.today()
# for num_day in range(8, 15):
#     button_day = (today + datetime.timedelta(days=num_day))
#     formatted = (format_date(button_day, format='EEEE, d MMMM', locale='ru')).capitalize()
#     print(formatted)
# print()
# for num_day in range(15, 22):
#     button_day = (today + datetime.timedelta(days=num_day))
#     formatted = (format_date(button_day, format='EEEE, d MMMM', locale='ru')).capitalize()
#     print(formatted)
#
# print()
#
# for num_day in range(22, 29):
#     button_day = (today + datetime.timedelta(days=num_day))
#     formatted = (format_date(button_day, format='EEEE, d MMMM', locale='ru')).capitalize()
#     print(formatted)


# open = datetime.time(7, 0, 0)
# close = datetime.time(22, 0, 0)
# duration = datetime.timedelta(minutes=60)
# open_timedelta = datetime.timedelta(hours=open.hour, minutes=open.minute)
# close_timedelta = datetime.timedelta(hours=close.hour, minutes=close.minute)
# print(open_timedelta, close_timedelta)
# diff = int(((close_timedelta-open_timedelta).total_seconds()) // 60)
# print(diff)
#
#
#
# for i in range(0, diff-60, 30):
#     incriment = datetime.timedelta(minutes=i)
#     start_timedelta = open_timedelta + incriment
#     end_timedelta = start_timedelta + duration
#     datetime_start = to_datetime(start_timedelta)
#     datetime_end = to_datetime(end_timedelta)
#
#
#     print(f'{datetime_start.strftime("%H:%M:%S")} to {datetime_end.strftime("%H:%M:%S")}')
#     print()
# #

