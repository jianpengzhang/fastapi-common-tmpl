from fastapi import FastAPI, HTTPException, status

from app import settings
from app.api.v1.api import api_router
from app.core.celery import do_health_check
from app.core.redis import get_redis_client
from app.core.utils import run_celery_task
from tortoise.contrib.fastapi import register_tortoise


# ========================================
# 说明: 入口
# 开发阶段启动命令：uvicorn app.main:app --host 0.0.0.0 --port <端口> --reload
# register_tortoise 是一个便捷函数，用于快速将 Tortoise-ORM 注册到 FastAPI 应用中。它在应用启动时初始化数据库连接，并在应用关闭时关闭连接。
# RegisterTortoise 是一个类，提供了更灵活和面向对象的方式来管理数据库连接。它允许你更精细地控制数据库初始化和关闭操作。

# @asynccontextmanager
# async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
#     # app startup
#     async with RegisterTortoise(
#         app,
#         db_url="sqlite://:memory:",
#         modules={"models": ["models"]},
#         generate_schemas=True,
#         add_exception_handlers=True,
#         use_tz=False,
#         timezone="Asia/Shanghai",
#     ):
#         # db connected
#         yield
#         # app teardown
#     # db connections closed

# app = FastAPI(title="Tortoise ORM FastAPI example", lifespan=lifespan)

# ========================================


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
    添加路由 (include_router): 将一个路由器 api_router 添加到 FastAPI 应用中;
    (1) api_router: 通常是定义了多个 API 端点的路由器实例;
    (2) prefix: 路由的前缀，所有包含在 api_router 中的路由都会以此前缀开始;
    """
    application.include_router(api_router, prefix=f"/api/{settings.VERSION}/examples")
    return application


# 这个 app 对象就是整个应用的入口，通常会传递给 ASGI 服务器（如 uvicorn）来运行。
app = get_application()


@app.get("/health/", summary="健康检查",
         description="Redis、Celery 服务检查",
         status_code=status.HTTP_200_OK,
         tags=["内置"])
async def health():
    # 内置：服务健康检查
    try:
        async with get_redis_client() as rs:
            # Ping Redis 服务器，检查连接状态
            if not await rs.ping():
                raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Redis health check failed")
            run_celery_task(do_health_check)
    except Exception:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Health check failed")
    return {"status": "ok"}
