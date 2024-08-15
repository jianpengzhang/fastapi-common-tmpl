import asyncio
import json
from typing import Dict, List, Any, Type

import redis.asyncio as aioredis
from fastapi import WebSocket, WebSocketDisconnect

from app.core.redis import get_redis_client
from app.core.utils import SingletonMeta


# ==========================================
# 说明: 定义 Websocket 基础类及自定义 Websocket
# ==========================================


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
        async with get_redis_client() as rs:
            await rs.publish(channel, message)

    async def connect(self) -> None:
        """
        初始化 Redis Pub/Sub 客户端
        :return:
        """
        async with get_redis_client() as rs:
            self.pubsub = rs.pubsub()

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
