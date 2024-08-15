import asyncio

from app.core.logger import LOG
from app.core.redis import acquire_lock, acquire_lock_with_retry, release_lock
from app.models.examples import ExampleUser, ExampleGroup
from app.schemas.examples import UserIn, GroupIn


# ========================================
# 说明: Service 层，封装复杂业务逻辑
# ========================================

# TODO：================= 用户 & 用户组 =======================#
class UserService:
    # TODO 示例：用户 Service

    @staticmethod
    async def create_user(user: UserIn):
        user_obj = await ExampleUser.create(**user.dict())
        return user_obj

    @staticmethod
    async def get_user(user_id: int):
        return await ExampleUser.filter(id=user_id).first()

    @staticmethod
    async def get_users():
        return await ExampleUser.all()

    @staticmethod
    async def update_user1(user_id: int):
        lock_key = f"example:user:{user_id}"
        if await acquire_lock(lock_key, 35):
            try:
                LOG.info("Succeeded to get redis lock")
                # 模拟长时间运行的任务
                await asyncio.sleep(30)
            finally:
                await release_lock(lock_key)
        else:
            LOG.info("Failed to get redis lock")

    @staticmethod
    async def update_user2(user_id: int):
        lock_key = f"example:user:{user_id}"
        if await acquire_lock_with_retry(lock_key, 35):
            try:
                LOG.info("Succeeded to get redis lock")
                # 模拟长时间运行的任务
                await asyncio.sleep(15)
            finally:
                await release_lock(lock_key)
        else:
            LOG.info("Failed to get redis lock")


class GroupService:
    # TODO 示例：用户组 Service

    @staticmethod
    async def create_group(group: GroupIn):
        group_obj = await ExampleGroup.create(**group.dict())
        return group_obj
