# from aiogram import Bot
# from decouple import config
# import psycopg



# def return_user(chat_id):
#     with psycopg.connect(config('CONN')) as conn:
#         with conn.cursor() as cursor:
#             cursor.execute(
#                 '''SELECT * FROM core_user WHERE telegram_id = %s;''',
#                 (chat_id,))
#             user = cursor.fetchone()
#             conn.close()
#             return user
#
#
# def register_user(*args):
#     with psycopg.connect(config('CONN')) as conn:
#         with conn.cursor() as cursor:
#             created_at = datetime.now()
#             if not args[4:]:
#                 cursor.execute(
#                     '''INSERT INTO core_user(telegram_id, phone, language, created_at) VALUES(%s, %s, %s, %s)
#                     RETURNING id;''',
#                     (args,))
#                 user_db = cursor.fetchone()
#             conn.close()
#             return user_db









token = config('TOKEN')
bot = Bot(token)