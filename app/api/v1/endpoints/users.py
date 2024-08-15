from fastapi import APIRouter, status, HTTPException

from app.models.examples import ExampleUser
from app.schemas.examples import UserUpdate, UserOut, UserIn
from app.services.examples import UserService

# ========================================
# 说明: 定义项目HTTP请求相关的路由；
# ========================================

router = APIRouter()


# TODO：================= 用户 API 接口 =======================#
@router.post("/", response_model=UserOut,
             summary="示例：创建用户",
             description="示例：创建用户 API 接口",
             responses={200: {"描述": "用户注册成功"}, }
             )
async def example_create_user(user: UserIn):
    # TODO 示例：创建用户，Service 层，封装复杂业务逻辑
    exam_user_obj = await UserService.create_user(user)
    return exam_user_obj


@router.get("/", response_model=list[UserOut],
            summary="示例：获取用户列表",
            description="示例：获取用户列表",
            status_code=status.HTTP_200_OK)
async def example_get_users():
    # TODO 示例：获取用户列表
    # 其他方式：return await Users_Pydantic.from_queryset(ExampleUser.all())
    return [UserOut.from_orm(user) for user in await ExampleUser.all()]


@router.get("/{user_id}", response_model=UserOut,
            summary="示例：根据用户 ID 检索用户",
            description="示例：根据用户 ID 检索 API 接口",
            status_code=status.HTTP_200_OK)
async def example_get_user(user_id: int):
    # TODO 示例：获取用户详情
    return await UserService.get_user(user_id)


@router.put("/{user_id}",
            response_model=UserOut,
            summary="示例：根据用户 ID 检索用户",
            description="示例：根据用户 ID 检索 API 接口",
            status_code=status.HTTP_200_OK)
async def example_update_user(user_id: int, user_in: UserUpdate):
    # TODO 示例：更新用户
    user = await ExampleUser.get(id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在，请联系管理员！")
    user = user.update_from_dict(user_in.dict(exclude_unset=True))
    await user.save()
    return UserOut.from_orm(user)


@router.delete("/{user_id}",
               response_model=dict,
               summary="示例：根据 ID 删除用户",
               description="示例：根据 ID 删除用户",
               status_code=status.HTTP_200_OK)
async def example_delete_user(user_id: int):
    # TODO 示例：删除用户
    user = await ExampleUser.get(id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在，请联系管理员！")
    await user.delete()
    return {"detail": "用户删除成功"}
