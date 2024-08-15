import asyncio
import contextlib
import time

import redis.asyncio as aioredis

from app import settings
from app.core.logger import LOG


# ========================================
# 说明: Redis 通用工具方法
#    * Redis Client 接口
#    * Redis 锁
# ========================================


@contextlib.asynccontextmanager
async def get_redis_client() -> aioredis.Redis:
    """
    基于异步上下文管理器获取和关闭 Redis 客户端
    :return:
    """
    rs = None
    try:
        # 异步 Redis 连接池，并设置 decode_responses=True：自动解码 Redis 响应为字符串（默认为字节）
        # max_connections=5000：连接池允许的最大连接数
        pool = aioredis.ConnectionPool.from_url(settings.BASE_REDIS,
                                                max_connections=5000,
                                                decode_responses=True)
        rs = aioredis.Redis(connection_pool=pool)
        yield rs
    except aioredis.RedisError as e:
        LOG.error(f"Failed to connect to Redis: {e}")
    finally:
        if rs:
            await rs.close()


async def acquire_lock(lock_key: str, timeout: int = 10) -> bool:
    """
    尝试获取锁:成功获取到锁，则返回 True，否则返回 False
    :param redis: Redis client
    :param lock_key: 锁对应健
    :param timeout: 设置键的过期时间（对应 ex） 单位 秒，
    :return: 锁获取成功 True

    Redis set 参数：
        （1）EX second ：设置键的过期时间（秒）；
        （2）PX millisecond ：设置键的过期时间（毫秒）；
        （3）NX ：只在键不存在时，才对键进行设置操作；
        （4）XX ：只在键已经存在时，才对键进行设置操作；
    """
    async with get_redis_client() as rs:
        result = await rs.set(lock_key, "locked", ex=timeout, nx=True)
        return result is not None


async def acquire_lock_with_retry(lock_key: str, timeout: int = 10,
                                  retry_interval: float = 0.1) -> bool:
    """
    指定超时时间内获取锁，如果成功获取到锁，则返回 True，否则，在超时时间内不断重试，直到超时时间结束。
    :param redis: Redis client
    :param lock_key: 锁对应健
    :param timeout: 设置键的过期时间（秒）以及 获取锁超时时间
    :param retry_interval: 重试间隔
    :return:
    """
    start_time = time.time()
    async with get_redis_client() as rs:
        while True:
            result = await rs.set(lock_key, "locked", ex=timeout, nx=True)
            if result:
                return True
            if time.time() - start_time >= timeout:
                return False
            LOG.info(f"Retry acquiring a redis lock... ...")
            await asyncio.sleep(retry_interval)


# async def release_lock(lock_key: str) -> None:
#     """
#     释放锁
#     :param redis:
#     :param lock_key:
#     :return:
#     """
#     with get_redis_client() as rs:
#         await rs.delete(lock_key)


async def release_lock(lock_key: str, lock_value: str = "locked") -> None:
    """
    释放锁：使用 Lua 脚本确保原子性删除锁，确保只有持有锁的客户端才能释放锁，这种方式可以防止误删除其他客户端持有的锁。
    :param redis:
    :param lock_key:
    :param lock_value:
    :return:
    """
    lua_script = """
    if redis.call("get", KEYS[1]) == ARGV[1] then
        return redis.call("del", KEYS[1])
    else
        return 0
    end
    """
    try:
        async with get_redis_client() as rs:
            sha = await rs.script_load(lua_script)
            await rs.evalsha(sha, 1, lock_key, lock_value)
    except aioredis.RedisError as e:
        LOG.error(f"Failed to release lock: {e}")
