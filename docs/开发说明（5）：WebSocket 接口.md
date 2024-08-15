# 开发说明（5）：WebSocket 接口

## 1. 说明

下面是如何使用 Redis 和 FastAPI 实现双向 WebSocket 通信，代码的核心是利用 Redis 的 Pub/Sub 机制在多个客户端之间进行消息广播和接收。

## 2. 创建 WebSocket 工具类

在项目 app/core/ 目录下，增加 websockets.py 工具库。

```
import asyncio
import json
from typing import Dict, List, Any, Type

import redis.asyncio as aioredis
from fastapi import WebSocket, WebSocketDisconnect

from app.core.redis import get_redis_client
from app.core.utils import SingletonMeta

class RedisPubSubManager:
    """
    管理 Redis 连接和 Pub/Sub 订阅的类;
    """

    def __init__(self, *args, **kwargs):
        self.pubsub = None

    @staticmethod
    async def _publish(channel: str, message: Any) -> None:
        """
        消息发布到指定的 Redis 频道（channel）
        :param channel: 消息频道名称
        :param message: 消息内容
        :return:
        """
        await redis_client._instance.redis.publish(channel, message)

    async def connect(self) -> None:
        """
        初始化 Redis Pub/Sub 客户端
        :return:
        """
        self.pubsub = redis_client._instance.redis.pubsub()

    async def subscribe(self, channel: str) -> aioredis.Redis:
        """
        订阅指定的 Redis 频道（channel）
        :param channel: 消息频道名称
        :return:
        """
        await self.pubsub.subscribe(channel)
        return self.pubsub

    async def unsubscribe(self, channel: str) -> None:
        """
        取消订阅指定的 Redis 频道（channel）
        :param channel: 消息频道名称
        :return:
        """
        await self.pubsub.unsubscribe(channel)


class WebSocketManager(RedisPubSubManager, metaclass=SingletonMeta):
    """
    管理 WebSocket Channel 连接；
    """

    channel = "default_channel"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.channels: Dict[str, List[WebSocket]] = {}

    async def _pubsub_data_reader(self, pubsub_subscriber):
        """
        不断读取 Redis 频道中的消息并广播到 频道（channel）中的所有 WebSocket 连接;
        注：get_message():
            {
            'type': 'message',
            'pattern': None,
            'channel': <Channel Name>,
            'data': '<Data>'
            }
        :param pubsub_subscriber:
        :return:
        """
        while True:
            #  获取来自 Redis 的消息，如果有新消息，解析消息并将其发送到相应channel内的所有 WebSocket 连接
            message = await pubsub_subscriber.get_message(ignore_subscribe_messages=True)
            if message is not None:
                all_sockets = self.channels[message['channel']]
                for socket in all_sockets:
                    await socket.send_text(message['data'])

    async def add_to_channel(self, channel: str, websocket: WebSocket) -> None:
        """
        将 Websocket 连接添加到频道（channel），并启动 Redis Pub/Sub 订阅
        :param channel: 消息频道名称
        :param websocket:
        :return:
        """
        await websocket.accept()
        if channel in self.channels:
            self.channels[channel].append(websocket)
        else:
            self.channels[channel] = [websocket]
            await self.connect()
            pubsub_subscriber = await self.subscribe(channel)
            # 创建一个任务，异步执行 _pubsub_data_reader()
            # _pubsub_data_reader() 可以在后台持续监听 Redis 消息，而不阻塞 WebSocket 连接的处理;
            asyncio.create_task(self._pubsub_data_reader(pubsub_subscriber))

    async def broadcast_to_channel(self, channel: str, message: Any) -> None:
        """
        将消息广播到channel中的所有 WebSocket 连接
        :param channel: 消息频道名称
        :param message: 消息内容
        :return:
        """
        await self._publish(channel, message)

    async def remove_from_channel(self, channel: str, websocket: WebSocket) -> None:
        """
        将 Websocket 从频道（channel）中移除，并在 频道（channel）为空时取消订阅 Redis 频道
        :param channel:
        :param websocket:
        :return:
        """
        self.channels[channel].remove(websocket)
        if len(self.channels[channel]) == 0:
            del self.channels[channel]
            await self.unsubscribe(channel)


class WebsocketConsumer:

    def __init__(self, websocket_class: Type[WebSocketManager]):
        if not callable(websocket_class):
            raise ValueError("Invalid websocket class")
        self.websocket_manager = websocket_class()

    async def connect(self, websocket: WebSocket, channel: str = None) -> None:
        """
        建立对应 Websocket 消息订阅
        :param websocket:
        :param channel:
        :return:
        """
        channel = channel or self.websocket_manager.channel
        await self.websocket_manager.add_to_channel(channel, websocket)
        try:
            while True:
                data = await websocket.receive_text()
                await self.websocket_manager.broadcast_to_channel(channel, data)
        except WebSocketDisconnect:
            await self.websocket_manager.remove_from_channel(channel, websocket)


# TODO：================= 自定义 Webocket =======================#

class ExampleWebsocket(WebSocketManager):
    """
    TODO 示例：自定义 WebSocket 示例
    """
    channel = "ws_example_channel"


class ExampleUserWebsocket(WebSocketManager):
    """
    TODO 示例：自定义 User WebSocket 示例
    """
    channel = "ws_example_user_channel_{}"

    async def broadcast_to_channel(self, channel: str, message: Any) -> None:
        """
        自定义消息结构体
        :param channel:
        :param message:
        :return:
        """
        data = {
            'type': 'user_event',
            'data': message
        }
        await self._publish(channel, json.dumps(data, ensure_ascii=False))
```

**代码说明：**

* (1). RedisPubSubManager 类
    * 功能: 管理 Redis 连接及其 Pub/Sub 订阅;
    * 方法:
      * _publish(channel, message): 将消息发布到指定的 Redis 频道;
      * connect(): 初始化 Redis Pub/Sub 客户端;
      * subscribe(channel): 订阅指定的 Redis 频道，并返回 pubsub 对象;
      * unsubscribe(channel): 取消订阅指定的 Redis 频道;

* (2). WebSocketManager 类
    * 功能: 继承 RedisPubSubManager，用于管理 WebSocket 连接和 Redis 通信;
    * 属性: __init__.channels 存储每个 Redis 频道和对应的 WebSocket 连接列表
    * 方法:
      * _pubsub_data_reader(pubsub_subscriber): 不断读取 Redis 频道中的消息并将其广播到所有连接到该频道的 WebSocket 客户端;
      * add_to_channel(channel, websocket): 将 WebSocket 连接添加到指定的频道，并启动 Redis Pub/Sub 订阅;
      * broadcast_to_channel(channel, message): 将消息广播到指定频道中所有 WebSocket 连接;
      * remove_from_channel(channel, websocket): 从频道中移除 WebSocket 连接，并在频道为空时取消订阅 Redis 频道;

* (3). WebsocketConsumer 类
    * 功能: 通用的 WebSocket 消息处理类;
    * 方法:
      * connect(websocket, channel): 建立 WebSocket 连接，接收来自客户端的消息，并将其广播到指定的频道;

* (4). 自定义 WebSocket 类
    * 功能: ExampleWebsocket 和 ExampleUserWebsocket 是两个自定义的 WebSocket 管理类;
    * ExampleWebsocket: 频道名称为 ws_example_channel;
    * ExampleUserWebsocket: 频道名称为 ws_example_user_channel_{}，带有用户标识符，并重写了 broadcast_to_channel 方法，以自定义消息的结构体;

**工作流程：**
    
* 当一个 WebSocket 客户端连接到服务器时，通过 WebsocketConsumer.connect() 方法处理连接;  
* 该方法会将 WebSocket 客户端添加到指定的 Redis 频道，并在该频道有新的消息发布时，将其广播到所有连接的客户端;  
* 如果客户端发送消息，该消息会被发布到 Redis 频道，随后通过 Redis 机制广播到所有订阅该频道的客户端;  
      
**使用场景：**

* 这种架构适用于需要在多个 WebSocket 客户端之间同步消息的场景，如聊天室、实时通知系统等;
* Redis Pub/Sub 机制确保了消息在所有订阅的客户端之间同步，WebSocket 保证了客户端与服务器的双向通信;

在项目 app/core/ 目录下，增加 utils.py 工具库，增加单例元类：

```
class SingletonMeta(type):
    """
    单例元类
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        方法重载，确保每次创建类的实例时，返回同一个实例;
        _instances，字典用于存储已经创建的实例
        :param args:
        :param kwargs:
        :return:
        """
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
```


## 3. 在 FastAPI 定义 ws 接口

在 app/api/v1/endpoints/ 中定义 ws 端点：

```
# app/api/v1/endpoints/websockets.py

from fastapi import APIRouter, WebSocket

from app.core.websockets import ExampleWebsocket, ExampleUserWebsocket, WebsocketConsumer


ws_router = APIRouter()


@ws_router.websocket(f"/{ExampleWebsocket.channel}")
async def websocket_endpoint(websocket: WebSocket):
    # TODO 示例：通用示例，对应 ExampleWebsocket 单例实现
    await WebsocketConsumer(ExampleWebsocket).connect(websocket)


@ws_router.websocket("/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    # TODO 示例： 不同用户ID不同消息频道，对应 ExampleUserWebsocket 单例实现
    channel = ExampleUserWebsocket.channel.format(user_id)
    await WebsocketConsumer(ExampleUserWebsocket).connect(websocket, channel)
```

在 app/main.py 中定义 ws 路由：

```
def get_application() -> FastAPI:
... ...
    application.include_router(user_router, prefix=f"/api/{settings.VERSION}/users")
    application.include_router(ws_router, prefix=f"/ws")
    return application
```

## 4. 定义周期性任务，定时 ws 消息推送

在 app/tasks/scheduler_tasks.py 中定义周期性 ws 消息推送任务：

```
from app.core.websockets import ExampleWebsocket

@shared_task()
def push_websocket_data():
    """
    # TODO 示例：定时推送 Websocket 消息
    """
    asyncio.run_coroutine_threadsafe(
        ExampleWebsocket().broadcast_to_channel(ExampleWebsocket.channel,
                                                f"TODO 示例：当前时间（周期任务）: {datetime.datetime.now().strftime('%Y-%m-%d  %H:%M:%S')}"),
        AsyncLoopCreator.get_loop())
```

在 app/core/celery_config.py 配置周期性任务：

```
# 配置任务周期性
beat_schedule = {
    'get_current_time': {
        'task': 'app.tasks.scheduler_tasks.get_current_time',
        'schedule': crontab(minute='*/1'),  # Every minute
    },
    'push_websocket_data': {
        'task': 'app.tasks.scheduler_tasks.push_websocket_data',
        'schedule': 5,
    },
}
```

## 5. 验证

* (1). 测试1：客户端（浏览器）推送消息至服务端：
  * 通过在线ws调试工具，例如：http://wstool.js.org/
    * ws 地址：`ws://<IP>:9001/ws/1`，点击“链接”；
    * 发送消息：`测试`；
    * 返回：`{"type": "user_event", "data": "测试"}`;

* (2). 测试2：服务端周期性推送消息至客户端（浏览器）：
  * 通过在线ws调试工具，例如：http://wstool.js.org/;
    * 监听 ws 地址：`ws://<IP>:9001/ws/ws_example_channel`;
    * 每隔 5s 收到消息：`TODO 示例：当前时间（周期任务）: 2024-08-14 17:41:31`;