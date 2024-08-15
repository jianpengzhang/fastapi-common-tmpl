import subprocess
import sys
import time

from app.config import TORTOISE_ORM
from app.models.examples import ExampleGroup, ExampleUser
from tortoise import Tortoise, run_async

# 内置 Group
BUILT_IN_GROUP = {
    "name": "系统管理",
    "description": "系统运维管理",
}

# 内置 User
BUILT_IN_USER = {
    "username": "Admin",
    "password": "Admin@123",
}


async def run_aerich_upgrade(retries: int = 3, delay: int = 5):
    """
    运行 `aerich upgrade` 进行数据库迁移, 默认尝试 3 次，间隔 5s
    :param retries: 最大重试次数
    :param delay: 每次重试之间的等待时间（秒）
    :return:
    """
    for attempt in range(1, retries + 1):
        try:
            subprocess.run(["aerich", "upgrade"], check=True)
            print("数据库迁移完成: aerich upgrade")
            break  # 如果成功，退出循环
        except subprocess.CalledProcessError as e:
            print(f"数据库迁移失败: {e}")
            if attempt < retries:
                print(f"将在 {delay} 秒后重试... (尝试 {attempt}/{retries})")
                time.sleep(delay)  # 等待一段时间后重试
            else:
                print("已达到最大重试次数，退出程序。")
                sys.exit(1)


async def init_group():
    """
    初始化：内置用户组
    :return:
    """
    try:
        if await ExampleGroup.filter(name=BUILT_IN_GROUP["name"]).exists():
            print(f"内置用户组已经存在: {BUILT_IN_GROUP['name']}")
        else:
            group = await ExampleGroup.create(**BUILT_IN_GROUP)
            print(f"内置用户组初始化成功: {group.name}")
    except Exception as e:
        raise e


async def init_user():
    """
    初始化：内置用户
    :return:
    """
    try:
        if await ExampleUser.filter(username=BUILT_IN_USER["username"]).exists():
            print(f"内置系统管理员已经存在: {BUILT_IN_USER['username']}")
        else:
            BUILT_IN_USER["group"] = await ExampleGroup.get(name=BUILT_IN_GROUP["name"])
            user = await ExampleUser.create(**BUILT_IN_USER)
            print(f"内置管理员初始化成功: {user.username}")
    except Exception as e:
        raise e


async def init_data():
    print("开始数据库初始化... ...")
    # 运行数据库迁移
    await run_aerich_upgrade()
    # 初始化数据库连接，使用从FastAPI应用配置中获取的信息
    try:
        await Tortoise.init(config=TORTOISE_ORM)
        await Tortoise.generate_schemas()
        # 执行数据初始化操作
        await init_group()
        await init_user()
    except Exception as e:
        print(f"数据库初始化失败: {e}")
        sys.exit(1)
    finally:
        await Tortoise.close_connections()
    print("数据库初始化完成")
    sys.exit(0)


def main():
    run_async(init_data())


if __name__ == '__main__':
    main()
