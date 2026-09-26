from __future__ import annotations

import asyncio
import datetime
from decimal import Decimal
from typing import Any, Optional, Sequence

import asyncpg
from decouple import config

from BronBot.utils import datetime_now

__all__ = [
    'init_pool', 'get_pool', 'close_pool', 'connect_db',
    'search_businesses_by_query', 'search_user_by_tg_id',
    'update_database_tg_id', 'search_businesses_by_category',
    'search_services_by_business', 'search_branches_by_business_id',
    'get_branch_info_by_id', 'business_name_by_id',
    'service_title_duration_and_price_by_id',
    'search_blocked_dates_by_business', 'search_working_hours_by_business_id',
    'search_staff_by_business_id', 'get_staff_name_and_position_by_staff_id',
    'products_by_business_id', 'products_info_by_ids',
    'create_booking', 'insert_booking_products',
    'search_bookings_for_profile', 'get_booking_details',
    'get_booking_products', 'block_date',
    'config', 'datetime_now',
]

_pool: Optional[asyncpg.Pool] = None
_pool_lock = asyncio.Lock()


def _connect_kwargs() -> dict:
    return {
        'host': config('DB_HOST', default='localhost'),
        'port': config('DB_PORT', default=5432, cast=int),
        'user': config('DB_USER'),
        'password': config('DB_PASSWORD'),
        'database': config('DB_NAME'),
    }


async def init_pool(**overrides: Any) -> asyncpg.Pool:
    """Create the shared pool.  Called once from __main__.py."""
    global _pool
    async with _pool_lock:
        if _pool is None:
            kwargs = _connect_kwargs()
            kwargs.update(
                min_size=config('DB_POOL_MIN', default=1, cast=int),
                max_size=config('DB_POOL_MAX', default=10, cast=int),
                command_timeout=60,
                # If a pgbouncer in transaction pooling mode is ever put in
                # front of this, uncomment the next line:
                # statement_cache_size=0,
            )
            kwargs.update(overrides)
            _pool = await asyncpg.create_pool(**kwargs)
    return _pool


async def get_pool() -> asyncpg.Pool:
    """Return the shared pool, creating it on first use."""
    if _pool is None:
        return await init_pool()
    return _pool


async def close_pool() -> None:
    """Close the shared pool on shutdown."""
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


async def connect_db() -> asyncpg.Pool:
    return await get_pool()


# --------------------------------------------------------------------------
# coercion helpers
# --------------------------------------------------------------------------

def _rows(records: Sequence[asyncpg.Record]) -> list:
    return [tuple(record) for record in records]


def _row(record: Optional[asyncpg.Record]) -> Optional[tuple]:
    return tuple(record) if record is not None else None


def _int(value: Any) -> Optional[int]:
    if value is None:
        return None
    elif type(value) is tuple:
        return int(value[0])
    return int(value)


def _dec(value: Any) -> Optional[Decimal]:
    if value is None:
        return None
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def _date(value: Any) -> Optional[datetime.date]:
    if value is None or isinstance(value, datetime.date) and not isinstance(value, datetime.datetime):
        return value
    if isinstance(value, datetime.datetime):
        return value.date()
    return datetime.date.fromisoformat(str(value))


def _time(value: Any) -> Optional[datetime.time]:
    if value is None or isinstance(value, datetime.time):
        return value
    if isinstance(value, datetime.datetime):
        return value.time()
    return datetime.time.fromisoformat(str(value))


def _timestamp(value: Any) -> Optional[datetime.datetime]:
    if value is None:
        return None
    if isinstance(value, str):
        value = datetime.datetime.fromisoformat(value)
    if value.tzinfo is None:
        from BronTelegramBot.utils import LOCAL_TZ
        value = value.replace(tzinfo=LOCAL_TZ)
    return value


# --------------------------------------------------------------------------
# businesses
# --------------------------------------------------------------------------

async def search_businesses_by_query(query: str):
    pool = await get_pool()
    records = await pool.fetch(
        """
        SELECT id, name
        FROM core_business
        WHERE name ILIKE '%' || $1 || '%'
        ORDER BY name
        """,
        (query or '').strip(),
    )
    return _rows(records)

async def get_categories():
    pool = await get_pool()
    records = await pool.fetch(
        """
        SELECT id, name
        FROM core_category
        ORDER BY name
        """
    )
    return _rows(records)

async def get_category_name_by_id(cat_id):
    pool = await get_pool()
    return await pool.fetchval(
        'SELECT name FROM core_category WHERE id = $1',
        _int(cat_id),
    )

async def search_businesses_by_category(category):
    pool = await get_pool()
    records = await pool.fetch(
        """
        SELECT id, name
        FROM core_business
        WHERE category_id = $1
        ORDER BY name
        """,
        str(category),
    )
    return _rows(records)


async def business_name_by_id(business_id):
    pool = await get_pool()
    return await pool.fetchval(
        'SELECT name FROM core_business WHERE id = $1',
        _int(business_id),
    )


# --------------------------------------------------------------------------
# users
# --------------------------------------------------------------------------

async def search_user_by_tg_id(telegram_id):
    pool = await get_pool()
    record = await pool.fetchrow(
        'SELECT id FROM core_user WHERE telegram_id = $1',
        _int(telegram_id)
    )
    return _row(record)


async def search_user_by_phone_number(phone_number):
    pool = await get_pool()
    record = await pool.fetchrow(
        'SELECT id FROM core_user WHERE phone = $1',
        phone_number)
    return _row(record)

async def update_database_tg_id(telegram_id, user_id):
    pool = await get_pool()
    await pool.execute(
        'UPDATE core_user SET telegram_id = $1 WHERE id = $2',
        _int(telegram_id), _int(user_id),
    )


# --------------------------------------------------------------------------
# branches, services, staff
# --------------------------------------------------------------------------

async def search_branches_by_business_id(business_id):
    pool = await get_pool()
    records = await pool.fetch(
        """
        SELECT id, name, address
        FROM core_branch
        WHERE business_id = $1
        ORDER BY name
        """,
        _int(business_id),
    )
    return _rows(records)


async def get_branch_info_by_id(branch_id):
    pool = await get_pool()
    record = await pool.fetchrow(
        'SELECT id, name, address FROM core_branch WHERE id = $1',
        _int(branch_id),
    )
    return _row(record)


async def search_services_by_business(business_id):
    pool = await get_pool()
    records = await pool.fetch(
        """
        SELECT id, title
        FROM core_service
        WHERE business_id = $1
        ORDER BY title
        """,
        _int(business_id),
    )
    return _rows(records)


async def service_title_duration_and_price_by_id(service_id):

    pool = await get_pool()
    record = await pool.fetchrow(
        'SELECT title, duration, price FROM core_service WHERE id = $1',
        _int(service_id),
    )
    return _row(record)


async def search_staff_by_business_id(business_id):
    pool = await get_pool()
    records = await pool.fetch(
        """
        SELECT id, full_name, position
        FROM core_staff
        WHERE business_id = $1 AND is_active
        ORDER BY full_name
        """,
        _int(business_id),
    )
    return _rows(records)


async def get_staff_name_and_position_by_staff_id(staff_id):
    pool = await get_pool()
    record = await pool.fetchrow(
        'SELECT full_name, position FROM core_staff WHERE id = $1',
        _int(staff_id),
    )
    return _row(record)


# --------------------------------------------------------------------------
# schedule
# --------------------------------------------------------------------------

async def search_blocked_dates_by_business(business_id):

    pool = await get_pool()
    records = await pool.fetch(
        """
        SELECT "date"
        FROM core_blockeddate
        WHERE business_id = $1
        ORDER BY "date"
        """,
        _int(business_id),
    )
    return _rows(records)


async def search_working_hours_by_business_id(business_id):

    pool = await get_pool()
    records = await pool.fetch(
        """
        SELECT day_of_week, is_closed, open_time, close_time
        FROM core_workinghours
        WHERE business_id = $1
        ORDER BY day_of_week
        """,
        _int(business_id),
    )
    return _rows(records)


async def block_date(*args):
    """Insert a blocked date.

    args: (date, reason, business_id, created_at)

    core_blockeddate has no unique constraint on (business_id, date), so
    the guard below stops the same date being inserted twice when several
    bookings land on one day.
    """
    booking_date, reason, business_id, created_at = args
    pool = await get_pool()
    await pool.execute(
        """
        INSERT INTO core_blockeddate ("date", reason, business_id, created_at)
        SELECT $1, $2, $3, $4
        WHERE NOT EXISTS (
            SELECT 1 FROM core_blockeddate
            WHERE business_id = $3 AND "date" = $1
        )
        """,
        _date(booking_date), reason, _int(business_id), _timestamp(created_at),
    )


# --------------------------------------------------------------------------
# products
# --------------------------------------------------------------------------

async def products_by_business_id(business_id):
    pool = await get_pool()
    records = await pool.fetch(
        """
        SELECT id, name, price
        FROM core_product
        WHERE business_id = $1 AND is_active
        ORDER BY name
        """,
        _int(business_id),
    )
    return _rows(records)


async def products_info_by_ids(product_id):
    pool = await get_pool()
    record = await pool.fetchrow(
        'SELECT id, name, price FROM core_product WHERE id = $1',
        _int(product_id),
    )
    return _row(record)


# --------------------------------------------------------------------------
# bookings
# --------------------------------------------------------------------------

async def create_booking(*args):
    (user_id, business_id, service_id, branch_id, total_price, guest_count,
     start_time, end_time, booking_date, notes, status, cancel_reason, attendance_status,
     created_at) = args

    pool = await get_pool()
    booking_id = await pool.fetchval(
        """
        INSERT INTO core_booking (
            user_id, business_id, service_id, branch_id,
            total_price, guest_count, start_time, end_time, booking_date,
            notes, status, cancel_reason, attendance_status, created_at)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
        RETURNING id
        """,
        _int(user_id), _int(business_id), _int(service_id), _int(branch_id),
        _dec(total_price), _int(guest_count), _time(start_time), _time(end_time),
        _date(booking_date), notes or '', str(status), cancel_reason or '', attendance_status or 'not_set',
        _timestamp(created_at),
    )
    return booking_id


async def insert_booking_products(*args):
    """args: (product_id, booking_id)"""
    product_id, booking_id = args
    pool = await get_pool()
    await pool.execute(
        """
        INSERT INTO core_booking_products (product_id, booking_id)
        VALUES ($1, $2)
        """,
        _int(product_id), _int(booking_id),
    )


async def search_bookings_for_profile(*args):
    """args: (user_id, status, status, ...)

    The aiosqlite version built this query with an f-string and wrapped
    the statuses in double quotes.  Postgres reads "confirmed" as an
    identifier, not a string literal, so that would raise
    UndefinedColumn.  Statuses are passed as an array parameter instead,
    which also accepts any number of them.
    """
    user_id, statuses = args[0], [str(status) for status in args[1:]]
    pool = await get_pool()
    records = await pool.fetch(
        """
        SELECT id, start_time, end_time, booking_date
        FROM core_booking
        WHERE user_id = $1 AND status = ANY($2::varchar[])
        ORDER BY booking_date ASC, start_time ASC
        """,
        _int(user_id), statuses,
    )
    return _rows(records)


async def get_booking_details(booking_id):
    pool = await get_pool()
    record = await pool.fetchrow(
        """
        SELECT user_id, business_id, service_id, branch_id, total_price,
               guest_count, start_time, end_time, booking_date, notes, status
        FROM core_booking
        WHERE id = $1
        """,
        _int(booking_id),
    )
    return _row(record)


async def get_booking_products(booking_id):
    pool = await get_pool()
    records = await pool.fetch(
        'SELECT product_id FROM core_booking_products WHERE booking_id = $1',
        _int(booking_id),
    )
    return _rows(records)
