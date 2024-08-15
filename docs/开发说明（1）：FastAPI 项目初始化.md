# 开发说明（1）：FastAPI 项目初始化

## 1. 说明

下面是关于如何基于 FastAPI Web 框架初始化一个 Demo 项目，包括项目结构及运行。

## 2. 项目结构

使用 FastAPI 实现微服务通常需要一个清晰的项目结构，以便于管理、扩展和维护。下面是一个典型的 FastAPI 项目初始化的目录结构，以及每个部分的详细说明。

实际可根据企业标准及开发规范灵活进行调整。

**项目目录结构:**

```
fastapi_demo/
├── app/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── security.py
│   │   └── celery_app.py
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── user.py
│   │   └── migrations/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── endpoints/
│   │   │   │   ├── __init__.py
│   │   │   │   └── user.py
│   │   │   ├── deps.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── user.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── user_service.py
│   ├── main.py
│   ├── logging_config.py
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py
│       └── test_user.py
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── pyproject.toml
└── README.md
```

**结构说明:**

* `app/`：项目的主目录，包含了所有应用程序的核心代码：
    * `app/core/`：包含应用程序的核心配置和工具模块；
      * `config.py`：存放项目配置，例如 环境变量、数据库连接字符串等；
      * `security.py`：安全相关配置和功能，例如 JWT 令牌生成与验证；
      * `celery_app.py`：Celery 配置，用于异步任务队列；
    * `app/db/`：用于管理数据库相关代码；
      * `base.py`：数据库基础模型；
      * `models/`：业务数据模型存放处；
      * `migrations/`：存放数据库迁移文件；
    * `app/api/`：用于管理 API 路由和端点；
      * `v1/`：版本化的 API 路由；
         * `endpoints/`：存放各个 API 端点；
    * `app/schemas/`：存放 Pydantic 模式定义，用于请求和响应数据的验证；
    * `app/services/`：用于存放业务逻辑处理代码，例如与数据库交互的服务层；
    * `app/main.py`：应用程序的入口，通常包含应用的实例化和启动逻辑；
    * `app/logging_config.py`：用于配置应用程序的日志记录；
    * `app/tests/`：包含所有的测试代码，使用 pytest 作为测试框架；
      * `conftest.py`：用于定义测试夹具（fixtures）;
      * `test_user.py`：用户相关的测试用例；
* `docker-compose.yml`：Docker Compose 配置文件，用于定义和管理多容器 Docker 应用程序；
* `Dockerfile`：Dockerfile 文件，用于构建应用的 Docker 镜像；
* `pyproject.toml`：项目配置文件；
* `requirements.txt`：项目依赖；
* `README.md`：项目的自述文件，通常用于记录项目简介、安装指南和使用说明；

* 其他注意事项：  
  (1) 版本控制：使用 Git 管理代码，创建不同的分支进行开发；  
  (2) 环境管理：推荐使用 .env 文件或环境变量来管理不同的配置（开发、测试、生产）；  
  (3) CI/CD 集成：可以集成 GitHub Actions、GitLab CI 等持续集成和部署工具；


**本 Demo 示例，目录结构:**

```Linux
$ tree -L 5
.
├── app
│ ├── api                           # Demo：Restful api 接口
│ │ └── v1
│ │     ├── api.py                  # Demo：路由注册
│ │     ├── endpoints
│ │     │ ├── groups.py             # Demo：Group CRUD 接口示例
│ │     │ ├── others.py             # Demo：Redis、Websocket、WS 接口示例
│ │     │ ├── users.py              # Demo：User CRUD 接口示例
│ │     │ └── websockets.py         # Demo：Websocket 接口示例
│ ├── config.py                     # Demo：App Config 配置
│ ├── core
│ │ ├── celery_config.py            # Demo：Celery Config 配置
│ │ ├── celery.py                   # Demo：Celery App 入口
│ │ ├── logger.py                   # Demo：Log 工作库
│ │ ├── redis.py                    # Demo：Redis 工作库
│ │ ├── utils.py                    # Demo：通用工具库
│ │ └── websockets.py               # Demo：基础类及自定义 Websocket
│ ├── main.py                       # Demo：App入口及内置健康检查 API
│ ├── models
│ │ ├── base.py                     # Demo：基础数据模型
│ │ └── examples.py                 # Demo：数据模型（User、Group）
│ ├── schemas
│ │ └── examples.py                 # Demo：定义数据模型 Pydantic 模式（schemas），用于在应用程序中进行数据验证和序列化/反序列化
│ ├── services
│ │ └── examples.py                 # Demo：Services 层示例
│ └── tasks
│     ├── scheduler_tasks.py        # Celery 定时任务
│     └── tasks.py                  # Celery 异步任务
├── docs                            # 开发说明
├── deploy
│ └── docker-compose
│     ├── docker-compose.yml        # docker-compose 部署 yaml 文件 
│     └── env.template              # 环境变量配置
├── Dockerfile                      # 构建容器镜像
├── LICENSE                         # LICENSE 授权
├── migrations                      # 迁移文件
├── pyproject.toml                  # 项目管理
├── README.md                       # 项目说明
├── requirements.txt                # Demo 依赖项
└── tests                           # 单侧用例
```

## 3. 项目初始化

最小化 FastAPI 项目示例代码。

#### 3.1  创建项目目录

```
ubuntu@jpzhang-dev:~/workspace/$ mkdir fastapi-common-tmpl
ubuntu@jpzhang-dev:~/workspace/$ cd fastapi-common-tmpl
ubuntu@jpzhang-dev:~/workspace/$ mkdir -p app/api/v1/endpoints
ubuntu@jpzhang-dev:~/workspace/$ mkdir -p app/core
... ...
```

#### 3.2  app/config.py - 配置文件


```
... ...

class Settings(BaseSettings):
    # 项目配置
    PROJECT_NAME: str = "fastapi-common-tmpl"
    PROJECT_DESCRIPTION: str = "基于 FastAPI 微服务通用基础框架"
    VERSION: str = "v1"
    DEBUG: bool = environ.get("DEBUG") == "true"
    TEST: bool = False  # environ.get("ENV") not in ["PROD", "DEV"]

    class Config:
        # 启用字段名称大小写敏感性 默认是 False
        case_sensitive = True
        
settings = Settings()            
```

#### 3.3  app/main.py - 主应用入口

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
    return application


# 这个 app 对象就是整个应用的入口，通常会传递给 ASGI 服务器（如 uvicorn）来运行。
app = get_application()


@app.get("/health/", summary="健康检查",
         description="Redis、Celery 服务检查",
         status_code=status.HTTP_200_OK,
         tags=["内置"])
async def health():
    #TODO 内置：服务健康检查
    return {"status": "ok"}
```


#### 3.4  安装依赖

**requirements.txt 文件：**

在项目根目录下创建 requirements.txt 文件（也可以通过 pyproject.toml 进行项目管理）：

```
fastapi==0.111.0
uvicorn==0.30.1
asyncpg==0.29.0
httpx==0.27.0
asgi-lifespan==2.1.0
... ...
```

**创建 Python 虚拟环境：**

```
ubuntu@jpzhang-dev:~/workspace/py-env$ python3.12 -m venv fastapi-common-tmpl 
ubuntu@jpzhang-dev:~/workspace/py-env$ source fastapi-common-tmpl/bin/activate
(fastapi-common-tmpl) ubuntu@jpzhang-dev:~/workspace/fastapi-common-tmpl$ pip install -r requirements.txt 
```

**运行应用：**

使用 uvicorn(高性能 ASGI 服务器) 启动应用:

```commandline
uvicorn app.main:app --reload --host 0.0.0.0 --port 9001
```
* `app.main:app :` 指定应用 app，"脚本名:FastAPI实例对象"；
* `--host:` 指定应用允许 IP 访问形式，默认：127.0.0.1；
* `--port:` 指定应用端口，默认为 8000；
* `--reload:` 自动重启，修改文件自动重启，用于开发阶段，生产阶段关闭；
* `--workers:` 指定工作进程数量，默认为 CPU 核心数的 1 倍，当同时设定 --reload 将无效；

更多参数，参考[官方文档](https://www.uvicorn.org/)；

**访问 API：**  
（1）服务健康检查 API 接口：`http://<IP>:9001/health/`    
（2）Swagger UI：`http://<IP>:9001/docs/`  

至此，完成 FastAPI Demo 项目初始化。