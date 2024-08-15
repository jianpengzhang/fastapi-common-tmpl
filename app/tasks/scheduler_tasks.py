import asyncio
import datetime

from celery import shared_task

from app.core.utils import AsyncLoopCreator
from app.core.websockets import ExampleWebsocket


# ========================================
# 说明: Celery 周期性任务
# ========================================


@shared_task()
def get_current_time():
    """
    # TODO 示例：定时获取当前时间
    """
    print(f"TODO 示例：当前时间（周期任务）: {datetime.datetime.now().strftime('%Y-%m-%d  %H:%M:%S')}")


@shared_task()
def push_websocket_data():
    """
    # TODO 示例：定时推送 Websocket 消息
    """
    asyncio.run_coroutine_threadsafe(
        ExampleWebsocket().broadcast_to_channel(ExampleWebsocket.channel,
                                                f"TODO 示例：当前时间（周期任务）: {datetime.datetime.now().strftime('%Y-%m-%d  %H:%M:%S')}"),
        AsyncLoopCreator.get_loop())