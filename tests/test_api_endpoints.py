import pytest
from httpx import AsyncClient

from app.main import app


@pytest.mark.anyio
async def test_user_crud(client: AsyncClient) -> None:
    # 创建 Group
    response = await client.post(app.url_path_for('example_create_group'),
                                 json={"name": "eg_group", "description": "This is description."})
    assert response.status_code == 200, response.text
    group_id = response.json()["id"]

    # 创建 User
    data = {
        "username": "eg_user",
        "nickname": "eg_nick_user",
        "email": "eg_user@example.com",
        "is_active": True,
        "is_superuser": False,
        "avatar": "/avatar/eg_user.png",
        "password": "123456",
        "group_id": group_id
    }

    response = await client.post(app.url_path_for('example_create_user'), json=data)
    assert response.status_code == 200, response.text
    user = response.json()
    assert user["username"] == "eg_user"
    user_id = user["id"]

    # 查询 User
    response = await client.get(app.url_path_for('example_get_user', user_id=user_id))
    assert response.status_code == 200, response.text
    user = response.json()
    assert user["username"] == "eg_user"

    # 查询 Users
    response = await client.get(app.url_path_for('example_get_users'))
    assert response.status_code == 200, response.text
    users = response.json()
    assert len([user for user in users if user.get("username") == "eg_user"]) == 1

    # 更新 User
    response = await client.put(app.url_path_for('example_update_user', user_id=user_id),
                                json={"username": "eg_update_user"})
    assert response.status_code == 200, response.text
    user = response.json()
    assert user["username"] == "eg_update_user"

    # 删除 User
    response = await client.delete(app.url_path_for('example_delete_user', user_id=user_id))
    assert response.status_code == 200, response.text
    assert "用户删除成功" in response.text


@pytest.mark.anyio
async def test_group_crud(client: AsyncClient) -> None:
    # 创建 Group
    data = {
        "name": "eg_group",
        "description": "This is description."
    }
    response = await client.post(app.url_path_for('example_create_group'), json=data)
    assert response.status_code == 200, response.text
    group = response.json()
    assert group["name"] == "eg_group"
    group_id = group["id"]

    # 查询 Group
    response = await client.get(app.url_path_for('example_get_group', group_id=group_id))
    assert response.status_code == 200, response.text
    group = response.json()
    assert group["name"] == "eg_group"

    # 查询 Groups
    response = await client.get(app.url_path_for('example_get_groups'))
    assert response.status_code == 200, response.text
    groups = response.json()
    assert len([group for group in groups if group.get("name") == "eg_group"]) == 1

    # 更新 Group
    data = {"name": "eg_update_group"}
    response = await client.put(app.url_path_for('example_update_group', group_id=group_id), json=data)
    assert response.status_code == 200, response.text
    group = response.json()
    assert group["name"] == "eg_update_group"

    # 删除 Group
    response = await client.delete(app.url_path_for('example_update_group', group_id=group_id))
    assert response.status_code == 200, response.text
    assert "用户组删除成功" in response.text
