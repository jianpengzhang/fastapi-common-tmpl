from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict


# ========================================
# 说明: 数据验证和数据解析
# ========================================


# TODO：================= 用户 =======================#

class BaseUser(BaseModel):
    # TODO 示例：基础
    username: Optional[str] = None
    nickname: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    avatar: Optional[str] = None


class UserIn(BaseUser):
    # TODO 示例：创建用户
    username: Optional[str]
    password: Optional[str]
    group_id: Optional[int]


class UserUpdate(UserIn):
    username: Optional[str] = None
    nickname: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    group_id: Optional[int] = None


class UserOut(BaseUser):
    # TODO 示例：用户详情
    id: int
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]

    model_config = ConfigDict(
        from_attributes=True
    )


# TODO：================= 用户组 =======================#
class GroupIn(BaseModel):
    # TODO 示例：创建用户组
    name: Optional[str] = None
    description: Optional[str] = None


class GroupOut(BaseModel):
    # TODO 示例：用户组详情
    id: int
    name: Optional[str]
    description: Optional[str]

    model_config = ConfigDict(
        from_attributes=True
    )


class GroupOutList(BaseModel):
    # TODO 示例：用户组列表
    total: int
    items: list[GroupOut]

    model_config = ConfigDict(
        from_attributes=True
    )
