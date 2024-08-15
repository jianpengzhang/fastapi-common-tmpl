# 开发说明（2）：PostgreSQL + Tortoise-ORM + Aerich

## 1. 说明

下面是关于如何使用 PostgreSQL、Tortoise ORM 和 Aerich 实现对象关系映射（ORM）及数据迁移。

## 2. 安装依赖

**requirements.txt 文件：** 新增依赖项：

```
asyncpg==0.29.0
tortoise-orm==0.21.3
aerich==0.7.2
```

* `tortoise-orm`：原生的异步 ORM，支持多种数据库，包括 PostgreSQL;
* `asyncpg`：用于与 PostgreSQL 数据库交互的异步 Python 库；
    * 异步驱动: asyncpg 是一个用于 Python 的异步 PostgreSQL 驱动，提供高性能异步 I/O 操作，使得它在需要处理大量并发请求的异步 Web 框架中非常高效；
    * 性能优势: 相较于传统的同步驱动（如 psycopg2），asyncpg 在异步场景中提供了更好的性能表现，因为它充分利用了 Python 的异步特性；
    * 使用场景: 适用于基于异步框架的应用程序，如 FastAPI、Sanic 或者任何基于 asyncio 的应用；
* `aerich`：Tortoise ORM 数据库迁移工具；

- 激活 Demo Python 虚拟环境：`$ source fastapi-common-tmpl/bin/activate`  
- 安装依赖：`$ pip install -r requirements.txt`

## 3. 配置 Tortoise ORM 和 PostgreSQL

在项目配置文件 app/config.py，增加用来管理 Tortoise ORM & PostgreSQL 的配置。

`app/config.py:`

```
class Settings(BaseSettings):
    ... ...
    # 数据库配置，优先读取环境变量，不存在则默认值
    POSTGRES_HOST: str = environ.get("POSTGRES_HOST") or "127.0.0.1"  # postgres
    POSTGRES_PORT: str = environ.get("POSTGRES_PORT") or "5432"
    POSTGRES_USER: str = environ.get("POSTGRES_USER") or "example"
    POSTGRES_PWD: str = environ.get("POSTGRES_PWD") or "example123"
    POSTGRES_DB: str = environ.get("POSTGRES_DB") or "fastapi_demo"
    DB_POOL_MAX: int = environ.get("DB_POOL_MAX") or 20
    DB_POOL_CONN_LIFE: int = environ.get("DB_POOL_CONN_LIFE") or 600
    TIMEZONE: str = environ.get("TIMEZONE") or "Asia/Shanghai"
    
    TORTOISE_ORM = {
        "connections": {
            "default": {
                "engine": "tortoise.backends.asyncpg",
                "credentials": {
                    "database": POSTGRES_DB,
                    "host": POSTGRES_HOST,
                    "password": POSTGRES_PWD,
                    "port": POSTGRES_PORT,
                    "user": POSTGRES_USER,
                    "maxsize": DB_POOL_MAX,  # 最大连接数
                    # "minsize": 1, # 最小连接数
                    # 关闭池中非活动连接的秒数。通过 0 则禁用此机制。
                    # "max_inactive_connection_lifetime": 60 * 5,
                    "ssl": False
                },
            }
        },
        "apps": {
            "models": {
                "models": ["aerich.models",
                           "app.models"],
                "default_connection": "default",
            }
        },
        "use_tz": False,
        "timezone": TIMEZONE
    }

settings = Settings()
TORTOISE_ORM = settings.TORTOISE_ORM
```

TORTOISE_ORM 是配置 Tortoise-ORM 数据库连接和模型的配置字典。

下面是每个参数的详细说明：

* `connections`: 定义了数据库连接信息，在这个配置中，你可以定义一个或多个连接，每个连接都有一个唯一的名称，例如 "default";
    * `default`: 表示默认的数据库连接名称;
      * `engine`: 指定使用的数据库引擎，这里使用的是 tortoise.backends.asyncpg，表示使用 asyncpg 作为 PostgreSQL 的异步驱动；
      * `credentials`: 连接数据库所需的凭据和参数；
        * `database`: 数据库名称，通常由环境变量 POSTGRES_DB 提供；
        * `host`: 数据库主机地址，通常由环境变量 POSTGRES_HOST 提供；
        * `password`: 数据库用户密码，通常由环境变量 POSTGRES_PWD 提供；
        * `port`: 数据库端口号，通常由环境变量 POSTGRES_PORT 提供，默认 5432；
        * `user`: 数据库用户名，通常由环境变量 POSTGRES_USER 提供； 
        * `maxsize`: 数据库连接池的最大连接数，通过设置 DB_POOL_MAX 环境变量来定义，这个值控制连接池中可以同时打开的最大连接数;
        * `minsize(可选)`: 数据库连接池的最小连接数，默认为 1，如果没有特别设置，连接池会在需要时自动调整到这个值；
        * `max_inactive_connection_lifetime(可选)`: 非活动连接在池中保持的最大时间（以秒为单位），设置为 0 时禁用此机制，连接将保持活动状态直到被使用或关闭；
        * `ssl`: 控制数据库连接是否启用 SSL 加密，设置为 False 表示不使用 SSL；
* `apps`: 定义了与数据库连接相关的应用程序及其模型；
    * `models`: 包含模型路径的列表；  
        * `aerich.models`: 包含 Aerich（数据库迁移工具）的内部模型，这是必须的，如果使用 Aerich 进行数据库迁移；
        * `app.models`: 应用程序模型所在的模块路径，例如这里 app.models； 
    * `default_connection`: 指定默认连接的名称。在这个例子中，设置为 "default"，即使用 "connections" 中的 "default" 连接； 
* `use_tz`: 设置为 True 时，Tortoise-ORM 会使用时区日期时间对象（带时区信息），设置为 False 时，将使用本地时间；
* `timezone`: 设置时区，通常与 TIMEZONE 环境变量相关联，如果 use_tz 为 True，此选项将指定使用的时区；

## 4. 定义模型

在 app/models/ 中定义数据库模型。例如，我们定义一个简单的用户模型：

```
# app/models/user.py
from tortoise import fields
from tortoise.models import Model


class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=50, unique=True)
    email = fields.CharField(max_length=255, unique=True)
    is_active = fields.BooleanField(default=True)

    class Meta:
        table = "users"

    def __str__(self):
        return self.username
```

在 app/models/__init__.py 文件中导入所有的模型，这样 Tortoise ORM 可以识别它们。

```
# app/models/__init__.py
from app.models.user import *
```

## 5. 设置 Aerich

**前提：** 运行一个 PostgreSQL 容器，例如：`docker-compose.yml 片段：

```
version: "2.3"
services:
  postgres:
    image: postgres:14.13
    command: postgres -c 'max_connections=1024'
    container_name: example-postgres
    restart: always
    volumes:
      - example-data-postgres:/var/lib/postgresql/data
    env_file:
      - .env
    networks:
      - example_net
    ports:
      - 5432:5432
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -h localhost -p 5432"]
      interval: 5s
      timeout: 5s
      retries: 5
... ...
networks:
  example_net:
    name: example_net
    external: false
volumes:
  example-data-postgres:
    name: example-data-postgres
    driver: local
    driver_opts:
      o: bind
      type: none
      device: /data/example/postgres
...            
```

PostgreSQL 实例：

```
(fastapi-common-tmpl) ubuntu@jpzhang-dev:~/workspace/fastapi-common-tmpl$ docker ps -a
CONTAINER ID   IMAGE                   COMMAND                   CREATED        STATUS                    PORTS                                       NAMES
306c4c60b5da   postgres:14.13          "docker-entrypoint.s…"   6 hours ago    Up 6 hours (healthy)      0.0.0.0:5432->5432/tcp, :::5432->5432/tcp   example-postgres
```

**设置 Aerich**

Aerich 是 Tortoise ORM 的数据库迁移工具，需要在项目根目录下初始化 Aerich。

```
$ aerich init -t app.config.TORTOISE_ORM

Success create migrate location ./migrations
Success write config to pyproject.toml
```

这将在项目根目录创建 pyproject.toml 文件，并在根目录下创建一个 migrations 文件夹。
接着，初始化数据库和迁移：

```
$ aerich init-db

Success create app migrate location migrations/models
Success generate schema for app "models"
```

## 6. 在 FastAPI 中集成 Tortoise ORM 

在 app/main.py 中配置和启动 FastAPI 应用时注册 Tortoise ORM：

```
def get_application() -> FastAPI:
    """
    创建和配置一个 FastAPI 应用程序
    :return:
    """

    """
    创建 FastAPI 实例
    (1) title: 应用的标题;
    (2) description: 应用的描述;
    (3) version: 应用的版本信息;
    (4) debug: 调试模式，通常在开发环境中开启，在生产环境中关闭;
    (5) openapi_tags: 自定义的 OpenAPI 标签，用于在 API 文档中组织和描述端点 
    """
    application = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.PROJECT_DESCRIPTION,
        version=settings.VERSION,
        debug=settings.DEBUG,
        openapi_tags=[
            {"name": "CRUD | PostgreSQL | Redis | WebSocket", "description": "示例"},
        ],
    )
    """
    使用 register_tortoise 函数将 Tortoise ORM 注册到 FastAPI 应用中;
    (1) application: 传递 FastAPI 应用实例;
    (2) config=settings.TORTOISE_ORM: 从 settings.TORTOISE_ORM 中获取 ORM 的配置（如数据库连接信息等）;
    (3) generate_schemas=True: 自动生成数据库表结构。通常在开发阶段使用，但在生产环境中最好禁用;
    (4) add_exception_handlers=True: 添加异常处理器，以便处理数据库相关的错误
    """
    register_tortoise(application, config=settings.TORTOISE_ORM,
                      generate_schemas=True, add_exception_handlers=True)
    """
    添加路由 (include_router): 将一个路由器 user_router 添加到 FastAPI 应用中;
    (1) api_router: 通常是定义了多个 API 端点的路由器实例;
    (2) prefix: 路由的前缀，所有包含在 api_router 中的路由都会以此前缀开始;
    """
    application.include_router(user_router, prefix=f"/api/{settings.VERSION}/users")               
    return application
```


## 7. 创建 API 端点

在 app/api/v1/endpoints/ 中定义用户的 API 端点。

```
# app/api/v1/endpoints/user.py
from fastapi import APIRouter, HTTPException
from app.schemas.user import UserCreate, UserResponse
from app.models.user import User

user_router = APIRouter()

@user_router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate):
    user_obj = await User.create(**user.dict())
    return user_obj

@user_router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    user = await User.filter(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

## 8. 定义 Pydantic 模式

在 app/schemas/user.py 中定义 Pydantic 模式。

```
# app/schemas/user.py
from pydantic import BaseModel


class UserBase(BaseModel):
    username: str
    email: str


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True
```

## 9. 运行迁移 

当修改了模型（比如添加了新的字段）时，需要使用 Aerich 管理数据库迁移。

生成迁移文件：

```
aerich migrate --name "add new fields to user"
```

应用迁移：

```
aerich upgrade
```

## 10. 启动应用 & 验证

**使用 uvicorn 启动应用程序：**

```
uvicorn app.main:app --reload --host 0.0.0.0 --port 9001
```

**验证：**

通过访问 `http://<IP>:9001/docs` 查看自动生成的 API 文档，并通过其中的接口来测试用户管理功能。

示例新增接口：

* 创建用户：`POST /api/v1/users/`
* 获取用户：`GET /api/v1/users/{user_id}`