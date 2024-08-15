from app.models.base import BaseDBModel
from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator


# ========================================
# 说明: 数据模型
# ========================================


# TODO：================= 用户 & 用户组 =======================#

class ExampleUser(BaseDBModel):
    """
    TODO 示例：用户
    """
    username = fields.CharField(max_length=20, unique=True, description="用户名")
    nickname = fields.CharField(max_length=50, null=True, description="昵称")
    email = fields.CharField(max_length=255, null=True, description="联系邮箱")
    password = fields.CharField(max_length=128, description="密码")
    last_login = fields.DatetimeField(null=True, description="上次登录")
    is_active = fields.BooleanField(default=True, description="是否活跃")
    is_superuser = fields.BooleanField(default=False, description="是否管理员")
    is_confirmed = fields.BooleanField(default=False, description="是否确认")
    avatar = fields.CharField(max_length=512, null=True, description="头像")
    group = fields.ForeignKeyField('models.ExampleGroup', related_name='example_user')

    class Meta:
        table = "example_user"
        table_description = "用例：用户"


class ExampleGroup(BaseDBModel):
    """
    TODO 示例：用户组
    """
    name = fields.CharField(max_length=50, unique=True)
    description = fields.TextField(null=True)

    class Meta:
        table = "example_group"
        table_description = "用例：用户组"


Users_Pydantic = pydantic_model_creator(ExampleUser, name="UserOutList")
