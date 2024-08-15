from typing import AsyncGenerator

import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from tortoise.transactions import in_transaction

from app.main import app


# ========================================
# 说明: 用于初始化创建和管理测试所需资源
# ========================================


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """
    pytest 使用 asyncio 作为事件循环
    :return:
    """
    return "asyncio"


@pytest.fixture(scope="session")
async def client() -> AsyncGenerator[AsyncClient, None]:
    """
    使用 httpx.AsyncClient 配合 LifespanManager 和 ASGITransport 创建一个测试客户端，用于发送 HTTP 请求;
    :return:
    """
    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            yield c


@pytest.fixture(autouse=True)
async def transaction():
    """
     确保每个测试用例在独立的事务中运行，测试结束后回滚事务，防止脏数据影响其他测试;
    :return:

    备注：
    @pytest.fixture(autouse=True) 该 fixture 会在每个测试用例执行前自动调用，无需显式引用；
    async with in_transaction() as conn：使用 Tortoise ORM 提供的 in_transaction() 上下文管理器创建一个新的数据库事务；
                                        in_transaction() 会返回一个事务连接 conn，该连接将在上下文管理器的作用范围内保持活动状态；
    yield conn ：yield 语句将事务连接对象 conn 暴露给测试用例，这允许测试用例在事务范围内执行数据库操作；
                在 yield 之前的代码会在测试用例执行前运行，yield 之后的代码会在测试用例执行完毕后运行；
    await conn.rollback()：在测试用例执行完毕后，回滚事务。这将撤销在事务中所做的所有数据库操作，从而确保测试数据不会保留在数据库中；
    """
    async with in_transaction() as conn:
        yield conn
        await conn.rollback()
