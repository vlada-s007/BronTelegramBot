import aiosqlite
from aiosqlite import Cursor
from BronTelegramBot.utils import datetime_now


#aiosqlite implementation for development
from decouple import config

# for pythonanywhere

async def connect_db():

    db = await aiosqlite.connect('/home/vlada007/BronTelegramBot/db.sqlite3')
    return db



# async def connect_db():

#     db = await aiosqlite.connect(config('db_path'))
#     return db


async def search_businesses_by_query(query: str):
    db = await connect_db()
    print(query)
    sqlq = f"SELECT id, name FROM core_business WHERE LOWER(name) LIKE '%{query.lower()}%'"
    #ILIKE for pgsql
    cursor: Cursor = await db.execute(sqlq)
    results = await cursor.fetchall()
    if not results:
        sqlq = f"SELECT id, name FROM core_business WHERE name LIKE '%{query.capitalize()}%'"
        cursor: Cursor = await db.execute(sqlq)
        results = await cursor.fetchall()
    await cursor.close()
    await db.close()
    return results

async def search_user_by_tg_id(telegram_id):
    db = await connect_db()
    cursor: Cursor = await db.execute("SELECT id FROM core_user WHERE telegram_id=?", (telegram_id,))
    results = await cursor.fetchone()
    print(results)
    await cursor.close()
    await db.close()
    return results

async def update_database_tg_id(telegram_id, user_id):
    db = await connect_db()
    cursor: Cursor = await db.execute("UPDATE core_user SET telegram_id=? WHERE id=?", (telegram_id, user_id))
    await db.commit()
    await cursor.close()
    await db.close()

async def search_businesses_by_category(category):
    db = await connect_db()
    cursor: Cursor = await db.execute("SELECT id, name FROM core_business WHERE category=?", (category,))
    results = await cursor.fetchall()
    await cursor.close()
    await db.close()
    return results

async def search_services_by_business(business_id):
    db = await connect_db()
    cursor: Cursor = await db.execute("SELECT id, title FROM core_service WHERE business_id=?", (business_id,))
    results = await cursor.fetchall()
    await cursor.close()
    await db.close()
    return results

async def search_branches_by_business_id(business_id):
    db = await connect_db()
    cursor: Cursor = await db.execute("SELECT id, name, address FROM core_branch WHERE business_id=?", (business_id,))
    results = await cursor.fetchall()
    await cursor.close()
    await db.close()
    return results

async def get_branch_info_by_id(branch_id):
    db = await connect_db()
    cursor: Cursor = await db.execute("SELECT id, name, address FROM core_branch WHERE id=?", (branch_id,))
    results = await cursor.fetchone()
    await cursor.close()
    await db.close()
    return results

async def business_name_by_id(business_id):
    db = await connect_db()
    cursor: Cursor = await db.execute("SELECT name FROM core_business WHERE id=?", (business_id,))
    results = await cursor.fetchone()
    await cursor.close()
    await db.close()
    return results[0]

async def service_title_duration_and_price_by_id(service_id):
    db = await connect_db()
    cursor: Cursor = await db.execute("SELECT title, duration, price FROM core_service WHERE id=?", (service_id,))
    results = await cursor.fetchone()
    await cursor.close()
    await db.close()
    return results

async def search_blocked_dates_by_business(business_id):
    db = await connect_db()
    print(business_id)
    cursor: Cursor = await db.execute('''SELECT date FROM core_blockeddate WHERE business_id=?''', (business_id,))
    results = await cursor.fetchall()
    print(results)
    await db.commit()
    await db.close()
    return results

async def search_working_hours_by_business_id(business_id):
    db = await connect_db()
    cursor: Cursor = await db.execute('''SELECT day_of_week, is_closed, open_time, close_time FROM core_workinghours WHERE business_id=?''', (business_id,))
    results = await cursor.fetchall()
    await db.commit()
    await db.close()
    return results

async def search_staff_by_business_id(business_id):
    db = await connect_db()
    cursor: Cursor = await db.execute("SELECT id, full_name, position FROM core_staff WHERE business_id=? AND is_active=1", (business_id,))
    results = await cursor.fetchall()
    await cursor.close()
    await db.close()
    return results

async def get_staff_name_and_position_by_staff_id(staff_id):
    db = await connect_db()
    cursor: Cursor = await db.execute("SELECT full_name, position FROM core_staff WHERE id=?", (staff_id,))
    results = await cursor.fetchone()
    await cursor.close()
    await db.close()
    return results

async def products_by_business_id(business_id):
    db = await connect_db()
    cursor: Cursor = await db.execute(
        '''SELECT id, name, price FROM core_product WHERE business_id=? AND is_active=1''', (business_id,))
    results = await cursor.fetchall()
    await cursor.close()
    await db.close()
    return results

async def products_info_by_ids(product_id):
    db = await connect_db()
    cursor: Cursor = await db.execute(
        '''SELECT id, name, price FROM core_product WHERE id=?''', (product_id,))
    results = await cursor.fetchone()
    await cursor.close()
    await db.close()
    return results

async def create_booking(*args):
    db = await connect_db()
    cursor: Cursor = await db.execute('''
    INSERT INTO core_booking(user_id, business_id, service_id, branch_id,
    total_price, guest_count, start_time, end_time, booking_date, notes, status, cancel_reason, created_at)
    VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', args)
    results = cursor.lastrowid
    print('inserted id is ' + str(results))
    await db.commit()
    await db.close()
    return results

async def insert_booking_products(*args):
    db = await connect_db()
    cursor: Cursor = await db.execute(
        'INSERT INTO core_booking_products(product_id, booking_id) VALUES(?, ?)', args)
    await db.commit()
    await db.close()

async def search_bookings_for_profile(*args):
    db = await connect_db()
    q = f'''SELECT id, start_time, end_time, booking_date
        FROM core_booking WHERE user_id={args[0]} AND (status="{args[1]}" OR status="{args[2]}")
        ORDER BY booking_date ASC, start_time ASC'''
    cursor: Cursor = await db.execute(q)
    results = await cursor.fetchall()
    await cursor.close()
    await db.close()
    return results


async def get_booking_details(booking_id):
    db = await connect_db()
    cursor: Cursor = await db.execute(
        '''SELECT user_id, business_id, service_id, branch_id, total_price,
        guest_count, start_time, end_time, booking_date, notes, status
        FROM core_booking WHERE id=?''', (booking_id,))
    results = await cursor.fetchone()
    await cursor.close()
    await db.close()
    return results


async def get_booking_products(booking_id):
    db = await connect_db()
    cursor: Cursor = await db.execute('''
    SELECT product_id FROM core_booking_products WHERE booking_id=?''', (booking_id,))
    results = await cursor.fetchall()
    await cursor.close()
    await db.close()
    return results

async def block_date(*args):
    db = await connect_db()
    cursor: Cursor = await db.execute('''INSERT INTO
    core_blockeddate(date, reason, business_id, created_at)
    VALUES(?, ?, ?, ?)''', args)
    await db.commit()
    await db.close()