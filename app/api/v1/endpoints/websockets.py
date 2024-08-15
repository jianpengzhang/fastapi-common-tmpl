from fastapi import APIRouter, WebSocket

from app.core.websockets import ExampleWebsocket, ExampleUserWebsocket, WebsocketConsumer

# ========================================
# 说明: 定义项目 Websocket 相关的路由；
# ========================================

router = APIRouter()


@router.websocket(f"/{ExampleWebsocket.channel}")
async def websocket_endpoint(websocket: WebSocket):
    # TODO 示例：通用示例，对应 ExampleWebsocket 单例实现
    await WebsocketConsumer(ExampleWebsocket).connect(websocket)


@router.websocket("/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    # TODO 示例： 不同用户ID不同消息频道，对应 ExampleUserWebsocket 单例实现
    channel = ExampleUserWebsocket.channel.format(user_id)
    await WebsocketConsumer(ExampleUserWebsocket).connect(websocket, channel)
