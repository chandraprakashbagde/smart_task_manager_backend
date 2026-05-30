"""
OTP Repository for managing OTP operations with the database.
Handles storage, retrieval, and updates of OTP records.
"""

from config import database
import aiomysql
from datetime import datetime

async def store_otp(email: str, otp_code: str, purpose: str, expiry_seconds: int) -> int:
    async with database.pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            query = """
            INSERT INTO otp_records (email, otp_code, purpose, expires_at)
            VALUES (%s, %s, %s, DATE_ADD(NOW(), INTERVAL %s SECOND))
            """
            await cursor.execute(query, (email, otp_code, purpose, expiry_seconds))
            await conn.commit()
            return cursor.lastrowid

async def get_latest_active_otp(email: str, purpose: str) -> dict:
    async with database.pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            query = """
            SELECT * FROM otp_records 
            WHERE email = %s 
            AND purpose = %s 
            AND is_used = 0 
            AND expires_at > NOW()
            ORDER BY created_at DESC 
            LIMIT 1
            """
            await cursor.execute(query, (email, purpose))
            result = await cursor.fetchone()
            return result

async def get_otp_by_id(otp_id: int) -> dict:
    async with database.pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            query = "SELECT * FROM otp_records WHERE otp_id = %s"
            await cursor.execute(query, (otp_id,))
            result = await cursor.fetchone()
            return result

async def mark_otp_as_used(otp_id: int) -> bool:
    async with database.pool.acquire() as conn:
        async with conn.cursor() as cursor:
            query = """
            UPDATE otp_records 
            SET is_used = 1, used_at = NOW()
            WHERE otp_id = %s
            """
            await cursor.execute(query, (otp_id,))
            await conn.commit()
            return cursor.rowcount > 0

async def get_last_otp_timestamp(email: str, purpose: str) -> datetime:
    """
    Get the creation timestamp of the most recent OTP (used or unused).
    Used for rate limiting/resend throttling.
    
    Args:
        email: User's email address
        purpose: OTP purpose
    
    Returns:
        Datetime of last OTP created, or None if no OTP exists
    """
    async with database.pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            query = """
            SELECT created_at as last_created_at FROM otp_records 
            WHERE email = %s AND purpose = %s order by created_at desc
            """
            await cursor.execute(query, (email, purpose))
            result = await cursor.fetchone()
            if result and result.get('last_created_at'):
                # Return the timestamp; MySQL TIMESTAMP is returned as datetime
                return result.get('last_created_at')
            return None

async def check_otp_rate_limit(email: str, purpose: str, wait_seconds: int) -> bool:
    """
    Check if user has exceeded rate limit for OTP requests.
    Uses database for timezone-safe comparison.
    
    Args:
        email: User's email
        purpose: OTP purpose
        wait_seconds: Required wait time in seconds
    
    Returns:
        True if rate limited, False if allowed
    """
    async with database.pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            query = """
            SELECT COUNT(*) as recent_count FROM otp_records 
            WHERE email = %s 
            AND purpose = %s 
            AND created_at > DATE_SUB(NOW(), INTERVAL %s SECOND)
            """
            await cursor.execute(query, (email, purpose, wait_seconds))
            result = await cursor.fetchone()
            # If there's a recent OTP, user is rate limited
            return result.get('recent_count', 0) > 0

async def cleanup_expired_otps() -> int:
    async with database.pool.acquire() as conn:
        async with conn.cursor() as cursor:
            query = "DELETE FROM otp_records WHERE expires_at < NOW()"
            await cursor.execute(query)
            await conn.commit()
            return cursor.rowcount
