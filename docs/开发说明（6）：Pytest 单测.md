# 开发说明（6）：Pytest 单测

## 1. 说明

下面是如何使用 Pytest 实现单元测试。

## 2. 安装依赖

**requirements.txt 文件：** 新增依赖项：

```
httpx==0.27.0
pytest-asyncio==0.23.7
pytest==8.2.2
pytest-cov==5.0.0
pytest-xdist==3.6.1
```

* 激活 Demo Python 虚拟环境：`$ source fastapi-common-tmpl/bin/activate`  
* 安装依赖：`$ pip install -r requirements.txt`

**【依赖项介绍】**

* (1). asgi-lifespan  
    asgi-lifespan 是一个 ASGI 中间件，它在应用程序生命周期的启动和关闭时提供钩子。
    对于 FastAPI 项目，它通常用于在测试中管理应用程序的生命周期，比如在测试开始时启动应用，在测试结束时关闭应用，具体来说，在使用 httpx 测试时，它确保了在请求之前应用已经启动，在请求之后应用可以被正确关闭。  

* (2). httpx  
    httpx 是一个支持异步操作的 HTTP 客户端，类似于 requests，但具有异步功能，它可以用来发出 HTTP 请求，用于测试 FastAPI 应用时非常方便。  
    使用 httpx.AsyncClient，可以模拟对 API 的请求，而不需要启动实际的服务器。  

* (3). pytest  
    pytest 是一个强大的 Python 测试框架，支持简单灵活的测试编写方式。

* (4). pytest-asyncio  
    pytest-asyncio 是 pytest 的插件，允许在测试中使用 asyncio 事件循环。通过这个插件，可以编写和测试异步代码。

* (5). pytest-cov  
    pytest-cov 是 pytest 的插件，用于生成测试覆盖率报告，可以检测代码有多少被测试用例覆盖，并生成详细的报告。

* (6). pytest-xdist   
    pytest-xdist 是 pytest 的插件，用于并行运行测试和在多台机器上分布测试负载，对于大型项目，运行时间较长的测试，pytest-xdist 可以极大地缩短测试运行时间。

## 3. 编写测试配置

在项目根路径下创建 tests 目录，并创建 conftest.py 用于设置测试环境，初始化数据库，创建 HTTP 客户端，以及管理数据库事务。

```
# app/tests/conftest.py

import pytest
from typing import AsyncGenerator
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from tortoise.transactions import in_transaction

from app.main import app

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
```

**代码解释：**

* (1). Fixture: anyio_backend

    ```
    @pytest.fixture(scope="session")
    def anyio_backend() -> str:
        return "asyncio"
    ```
  
   * 作用: 该 fixture 设置 pytest 的异步测试环境，指定使用 asyncio 作为异步运行的后端;
   * 返回值: 字符串 "asyncio"，指示 pytest 使用 asyncio 事件循环，而 asyncio 是 Python 的内建异步 I/O 框架；
   * 作用范围: session 表示该 fixture 在整个测试会话期间只会被执行一次；

* (2). Fixture: client
    ```
    @pytest.fixture(scope="session")
    async def client() -> AsyncGenerator[AsyncClient, None]:
        async with LifespanManager(app):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as c:
                yield c
    ```
    * 作用: 
      * 创建一个 httpx 的 AsyncClient 实例，用于发送 HTTP 请求。这个客户端使用了 LifespanManager 来管理 FastAPI 应用的生命周期，确保应用在测试期间正确启动和关闭；
      * 使用 ASGITransport 将请求直接发送到 FastAPI 应用，而不是通过网络，这加快了测试速度；
      * base_url="http://test": 设置客户端的基础 URL；
    * 作用范围: session 表示该 fixture 在整个测试会话期间只会被执行一次；
    * 返回值: 异步生成器，生成 AsyncClient 实例；

* (3). Fixture: transaction
    ```
    @pytest.fixture(autouse=True)
    async def transaction():
        async with in_transaction() as conn:
            yield conn
            await conn.rollback()
    ```
    * 作用: 保证每个测试用例在一个独立的数据库事务中运行，并在测试结束后回滚事务，确保数据库不被污染;
    * in_transaction(): Tortoise ORM 提供的上下文管理器，用于创建一个新的数据库事务，async with in_transaction() 确保在该上下文内执行的所有数据库操作都被事务控制;
    * yield conn: 在 yield 之前的部分，创建并开启一个数据库事务，并将事务连接对象 conn 暴露给测试用例使用，测试用例在 yield 之后执行;
    * await conn.rollback(): 在 yield 之后部分，回滚该事务，撤销在事务内执行的所有数据库操作，防止脏数据影响其他测试;
    * 自动使用: autouse=True 表示该 fixture 会自动应用于所有测试用例，无需显式调用;

## 4. 编写测试用例

在项目 tests 目录下，创建 test_api_endpoints.py 测试用例文件。

```
import pytest
import json
from httpx import AsyncClient

from app.main import app


@pytest.mark.anyio
async def test_user_create_get(client: AsyncClient) -> None:
    # 创建用户
    response = await client.post(app.url_path_for('create_user'),
                                 json={"username": "jpzhang", "email": "jpzhang.ht@gmail.com"})

    assert response.status_code == 200, response.text
    user_id = json.loads(response.text)["id"]

    # 查询用户
    response = await client.get(app.url_path_for('get_user', user_id=user_id))

    assert response.status_code == 200, response.text
    assert json.loads(response.text)["username"] == "jpzhang"
```

项目根路径下执行测试：

```
pytest -s -n 4 --cov=. --cov-report term --cov-report xml:coverage.xml --junitxml=report.xml
```