import asyncio
import asyncpg
import logging
from typing import Optional
from contextlib import asynccontextmanager
from server.config.settings import settings

logger = logging.getLogger(__name__)

# Module-level pool variable initialized to None
_pool: Optional[asyncpg.Pool] = None
_pool_lock = asyncio.Lock()  # H9: prevent race on concurrent startup

async def get_pool() -> asyncpg.Pool:
    global _pool
    async with _pool_lock:
        if _pool is None:
            logger.info("Initializing database connection pool.")
            _pool = await asyncpg.create_pool(
                settings.database_url,
                min_size=2,
                max_size=10
            )
    return _pool

async def close_pool():
    global _pool
    if _pool is not None:
        logger.info("Closing database connection pool.")
        await _pool.close()
        _pool = None

@asynccontextmanager
async def get_connection():
    pool = await get_pool()
    async with pool.acquire() as conn:
        yield conn
