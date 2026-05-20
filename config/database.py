import aiomysql
from .config import setting

pool = None

async def init_db():
    global pool 
    pool = await aiomysql.create_pool(
        host=setting.DB_HOST,
        port=setting.DB_PORT,
        user=setting.DB_USER,
        password=setting.DB_PASSWORD,
        db=setting.DB_NAME,
        minsize=1,
        maxsize=10,
        autocommit=False
    )

async def close_db():
    global pool
    pool.close()

    await pool.wait_closed()