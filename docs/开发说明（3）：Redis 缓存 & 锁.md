# 开发说明（3）：Redis 缓存 & 锁

## 1. 说明

下面是关于如何集成 Redis 并通过异步 Redis 连接池提供缓存和分布式锁工具类示例说明。

## 2. 安装依赖

**requirements.txt 文件：** 新增依赖项：

```
redis==5.0.5
```

* 激活 Demo Python 虚拟环境：`$ source fastapi-common-tmpl/bin/activate`  
* 安装依赖：`$ pip install -r requirements.txt`

## 3. 配置 Redis 连接

在项目配置文件 app/config.py，增加 Redis 链接配置。

`app/config.py:`

```
class Settings(BaseSettings):
    ... ...
    
    # Redis 配置
    REDIS_HOST: str = environ.get("REDIS_HOST") or "127.0.0.1"  # redis
    REDIS_PORT: str = environ.get("REDIS_PORT") or "6379"
    REDIS_USER: str = environ.get("REDIS_USER") or ""
    REDIS_PWD: str = environ.get("REDIS_PWD") or ""
    # 0 库用于后端，1 库用于celery broker
    BASE_REDIS: str = f"redis://{REDIS_USER}:{REDIS_PWD}@{REDIS_HOST}:{REDIS_PORT}/"

    class Config:
        # 启用字段名称大小写敏感性 默认是 False
        case_sensitive = True
        
settings = Settings()
```

## 4. 创建 Redis 客户端工具类 

创建一个 Redis 客户端工具类，用于缓存和分布式锁的实现。

```
class RedisClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # 初始化连接池
            cls._instance.pool = aioredis.ConnectionPool.from_url(
                settings.BASE_REDIS,
                max_connections=5000,
                decode_responses=True
            )
            cls._instance.redis = aioredis.Redis(connection_pool=cls._instance.pool)
        return cls._instance

    async def get(self, key: str) -> Optional[Any]:
        """
        从 Redis 中获取键值，并将其从 JSON 格式解析为 Python 对象。
        :param key: 键名
        :return: 键对应的值，如果键不存在则返回 None
        """    
        value = await self.redis.get(key)
        if value is not None:
            return json.loads(value)
        return None
        
    async def set(self, key: str, value: Any, expire: int = 3600) -> None:
        """
        将值存储到 Redis 中，并设置过期时间。
        :param key: 键名
        :param value: 要存储的值，必须是可序列化为 JSON 的对象
        :param expire: 过期时间，单位为秒
        """
        value = json.dumps(value)
        await self.redis.set(key, value, ex=expire)

    async def delete(self, key: str) -> None:
        """
        从 Redis 中删除键。
        :param key: 键名
        """        
        await self.redis.delete(key)

    @contextlib.asynccontextmanager
    async def lock(self, key: str, expire: int = 10):
        """
        创建一个分布式锁，并使用上下文管理器控制锁的获取与释放。
        :param key: 锁的键名
        :param expire: 锁的过期时间，单位为秒
        """        
        is_locked = await self.redis.set(key, "1", ex=expire, nx=True)
        try:
            if is_locked:
                yield # 成功获取锁，继续执行上下文中的代码
            else:
                raise Exception("Unable to acquire lock") # 未能获取锁，抛出异常
        finally:
            if is_locked:
                await self.delete(key) # 释放锁
              
    async def acquire_lock_with_timeout(self, key: str, timeout: int, expire: int = 10) -> bool:
        """
        在指定的超时时间内尝试获取锁，如果获取到锁则返回 True，否则返回 False。
        :param key: 锁的键名
        :param timeout: 尝试获取锁的超时时间，单位为秒
        :param expire: 锁的过期时间，单位为秒
        :return: 成功获取到锁返回 True，否则返回 False
        """
        end_time = asyncio.get_event_loop().time() + timeout
        while True:
            is_locked = await self.redis.set(key, "1", ex=expire, nx=True)
            if is_locked:
                return True
            if asyncio.get_event_loop().time() > end_time:
                break
            await asyncio.sleep(0.1)  # 等待 100 毫秒后重试
        return False

    async def try_acquire_lock(self, key: str, expire: int = 10) -> bool:
        """
        尝试获取锁，如果成功获取到锁则返回 True，否则返回 False。
        :param key: 锁的键名
        :param expire: 锁的过期时间，单位为秒
        :return: 成功获取到锁返回 True，否则返回 False
        """
        return await self.redis.set(key, "1", ex=expire, nx=True)

    async def release_lock(self, key: str, lock_value: str = "locked") -> None:
        """
        释放锁，删除 Redis 中的锁键。
        :param key: 锁的键名
        """
        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        try:
            sha = await self.redis.script_load(lua_script)
            await self.redis.evalsha(sha, 1, key, lock_value)
        except aioredis.RedisError as e:
            LOG.error(f"Failed to release lock: {e}")


# 创建 RedisClient 实例
redis_client = RedisClient()
```

**代码解释：**

* (1). __new__ 方法：  
    * 目的：RedisClient 类采用单例模式，确保整个应用程序中只存在一个 Redis 连接池实例，有效减少 Redis 连接开销；  
    * 参数：   
        `decode_responses=True`：自动解码 Redis 响应为字符串（默认为字节）；  
        `max_connections=5000`：连接池允许的最大连接数;
    
* (2). get 方法：  
    * 目的: 从 Redis 中获取一个键的值，并将其解析为 Python 对象；
    * 返回值: 如果键存在，返回其值，否则返回 None；
        
* (3). set 方法：  
    * 目的: 将一个键值对存储到 Redis 中，并指定过期时间;
    * JSON 序列化: 值被序列化为 JSON 格式以便存储，这使得可以存储复杂的 Python 对象;

* (4). delete 方法：  
    * 目的: 从 Redis 中删除一个键;

* (5). lock 方法：  
    * 目的: 提供一个上下文管理器来获取和释放分布式锁;  
    * nx=True: 确保锁只有在键不存在时才能设置，这防止多个客户端同时获得相同的锁;  
    * 上下文管理(@contextlib.asynccontextmanager): 如果成功获取到锁，执行上下文代码，否则抛出异常，上下文结束时自动释放锁;  

* (6). acquire_lock_with_timeout 方法：    
    * 目的: 在指定时间内不断尝试获取锁，适用于需要在指定时间内保证操作成功的场景;  
    * 重试逻辑: 使用 asyncio.sleep 在失败时短暂休眠后重试，直到超时或成功获取锁;  
    * 返回值: 成功获取锁返回 True，否则返回 False;  

* (7). try_acquire_lock 方法：  
    * 目的: 立即尝试获取锁，适用于不需要等待的场景;  
    * 返回值: 成功获取锁返回 True，否则返回 False;  

* (8). try_acquire_lock 方法：  
    * 目的: 使用 Lua 脚本保证锁的安全释放，确保只有持有锁的客户端才能删除锁;    


## 5.  创建 API 端点

在 app/api/v1/endpoints/ 中定义 API 端点，验证 Redis 工具类，可创建新的接口文件或在已有文件中加入如下代码：

* (1) 指定超时时间内不断重试获取锁
    ```
    # app/api/v1/endpoints/user.py

    @user_router.post("/perform-action/")
    async def perform_action(user_id: int):
        lock_key = f"user:{user_id}:lock"
        # 尝试在 5 秒内获取锁
        if await redis_client.acquire_lock_with_timeout(lock_key, timeout=5, expire=10):
            try:
                # 执行需要加锁的操作
                return {"status": "success"}
            finally:
                # 释放锁
                await redis_client.release_lock(lock_key)
        else:
            raise HTTPException(status_code=423, detail="Could not acquire lock")
    ```
* (2) 尝试获取锁立即返回结果
    ```
    # app/api/v1/endpoints/user.py

    @user_router.post("/attempt-action/")
    async def attempt_action(user_id: int):
        lock_key = f"user:{user_id}:lock"
        # 尝试获取锁
        if await redis_client.try_acquire_lock(lock_key, expire=10):
            try:
                # 执行需要加锁的操作
                return {"status": "success"}
            finally:
                # 释放锁
                await redis_client.release_lock(lock_key)
        else:
            return {"status": "failed", "detail": "Could not acquire lock"}
    ```

通过访问 `http://<IP>:9001/docs` 查看自动生成的 API 文档，并通过其中的接口来测试 Redis 功能。

示例新增接口：

* 带超时的锁：`POST /api/v1/users/perform-action/`

* 立即尝试获取锁：`POST /api/v1/users/attempt-action/` 
 
【注意】：
* `acquire_lock_with_timeout` 方法：会在指定的超时时间内不断尝试获取锁，如果在超时时间内获取到锁，则返回 True，否则返回 False;  
* `try_acquire_lock` 方法：会立即尝试获取锁，如果成功获取到锁，则返回 True，否则返回 False;