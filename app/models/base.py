from tortoise import models, fields


# ========================================
# 说明: 基础数据模型
# ========================================


class BaseDBModel(models.Model):
    """
    TODO 示例：基础数据模型
    """
    id = fields.BigIntField(primary_key=True, db_index=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        abstract = True
