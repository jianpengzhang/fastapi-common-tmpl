import datetime

from fastapi import APIRouter, status

from app.core.logger import LOG
from app.core.redis import get_redis_client
from app.core.utils import run_celery_task
from app.core.websockets import ExampleWebsocket
from app.services.examples import UserService
from app.tasks import tasks

# ========================================
# 说明: 定义项目HTTP请求相关的路由；
# ========================================

router = APIRouter()


# TODO：================= Celery Task =======================#
@router.get("/tasks",
            summary="示例：异步任务",
            description="示例：异步任务",
            status_code=status.HTTP_200_OK,
            responses={404: {"描述": "异步任务"}, }
            )
async def example_exec_tasks():
    # TODO 示例：异步任务
    run_celery_task(tasks.eg_task)
    return {"Exec tasks": "ok"}


# TODO：================= Redis =======================#
@router.get("/redis/cache",
            summary="示例：Redis 操作（缓存）",
            description="示例：Redis 操作（缓存）",
            status_code=status.HTTP_200_OK,
            responses={404: {"描述": "Redis 操作（缓存）"}, }
            )
async def example_exec_redis_with_cache():
    # TODO 示例：Redis 缓存
    async with get_redis_client() as rs:
        await rs.set('example_redis', 'Hello, Redis!')
        LOG.info(f"【** Example **】Redis key(example_redis) stored value:{await rs.get('example_redis')}")
    return {"Exec redis (Cache)": "ok"}


@router.get("/redis/lock/1",
            summary="示例：Redis lock 操作（简单锁）",
            description="示例：Redis lock 操作",
            status_code=status.HTTP_200_OK,
            responses={404: {"描述": "Redis lock 操作"}, }
            )
async def example_exec_redis_with_lock1():
    # TODO 示例：Redis lock 操作
    await UserService.update_user1(user_id=10)
    return {"Exec redis (lock)": "ok"}


@router.get("/redis/lock/2",
            summary="示例：Redis lock 操作（重试获取，直至超时）",
            description="示例：Redis lock 操作",
            status_code=status.HTTP_200_OK,
            responses={404: {"描述": "Redis lock 操作"}, }
            )
async def example_exec_redis_with_lock2():
    # TODO 示例：Redis lock 操作
    await UserService.update_user2(user_id=20)
    return {"Exec redis (lock)": "ok"}


# TODO：================= Websocket =======================#
@router.get(f"/ws/push",
            summary="示例：模拟 ws 推送",
            description="示例：模拟触发后端发送 ws 推送，通过在线 ws 工具监听 ws_example_channel，然后调用接口手动触发",
            status_code=status.HTTP_200_OK,
            responses={404: {"描述": "模拟 ws 推送"}, }
            )
async def example_exec_ws_push():
    # TODO 示例：模拟 ws 推送
    await ExampleWebsocket().broadcast_to_channel(channel=ExampleWebsocket.channel,
                                                  message=f"TODO 示例（WS 推送）：当前时间（周期任务）: {datetime.datetime.now().strftime('%Y-%m-%d  %H:%M:%S')}")
    return {"Push ws": "ok"}
