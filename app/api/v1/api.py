from fastapi import APIRouter

from app.api.v1.endpoints import users, groups, others, websockets

# ========================================
# 说明: 路由引入
# ========================================

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(groups.router, prefix="/groups", tags=["Groups"])
api_router.include_router(others.router, prefix="/others", tags=["Others"])
api_router.include_router(websockets.router, prefix="/ws", tags=["ws"])
