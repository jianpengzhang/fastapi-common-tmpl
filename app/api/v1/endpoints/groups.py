from fastapi import APIRouter, status, HTTPException

from app.models.examples import ExampleGroup
from app.schemas.examples import GroupIn, GroupOut
from app.services.examples import GroupService

# ========================================
# 说明: 定义项目HTTP请求相关的路由；
# ========================================

router = APIRouter()


@router.post("/", response_model=GroupOut,
             summary="示例：创建用户组",
             description="示例：创建用户组 API 接口",
             responses={status.HTTP_200_OK: {"描述": "用户组创建成功"}, }
             )
async def example_create_group(group: GroupIn):
    # TODO 示例：创建用户组
    exam_group_obj = await GroupService.create_group(group)
    return exam_group_obj


@router.get("/", response_model=list[GroupOut],
            summary="示例：获取用户组列表",
            description="示例：获取用户组列表",
            responses={status.HTTP_200_OK: {"描述": "获取用户组列表"}, }
            )
async def example_get_groups():
    # TODO 示例：获取用户组列表
    return [GroupOut.from_orm(group) for group in await ExampleGroup.all()]


@router.get("/{group_id}", response_model=GroupOut,
            summary="示例：获取指定ID用户组",
            description="示例：获取指定ID用户组",
            responses={status.HTTP_200_OK: {"描述": "获取指定ID用户组"}, }
            )
async def example_get_group(group_id: int):
    # TODO 示例：获取指定 ID 用户组
    return await ExampleGroup.filter(id=group_id).first()


@router.put("/{group_id}", response_model=GroupOut,
            summary="示例：更新指定ID用户组",
            description="示例：更新指定ID用户组",
            responses={status.HTTP_200_OK: {"描述": "更新指定ID用户组"}, }
            )
async def example_update_group(group_id: int, group_in: GroupIn):
    # TODO 示例：更新指定 ID 用户组
    group = await ExampleGroup.get(id=group_id)
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户组不存在，请联系管理员！")
    group = group.update_from_dict(group_in.dict(exclude_unset=True))
    await group.save()
    return GroupOut.from_orm(group)


@router.delete("/{group_id}",
               response_model=dict,
               summary="示例：根据 ID 删除用户组",
               description="示例：根据 ID 删除用户组",
               status_code=status.HTTP_200_OK)
async def example_delete_group(group_id: int):
    # TODO 示例：删除用户组
    group = await ExampleGroup.get(id=group_id)
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户组不存在，请联系管理员！")
    await group.delete()
    return {"detail": "用户组删除成功"}
