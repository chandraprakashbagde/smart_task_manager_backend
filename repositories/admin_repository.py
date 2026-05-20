from config import database
import aiomysql
from config.config import setting


async def create_admin():
    async with database.pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            pass