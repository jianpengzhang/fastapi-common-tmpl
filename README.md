# FastAPI Examples

基于 FastAPI 框架，展示 FastAPI + Tortoise-ORM + Celery + Websocket + Redis + PostgreSQL 搭配构建一个简单异步微服务 Demo 示例；

开发文档：`./docs`:

* 开发说明（1）：FastAPI 项目初始化
* 开发说明（2）：PostgreSQL + Tortoise-ORM + Aerich 数据映射及管理
* 开发说明（3）：Redis 缓存 & 锁
* 开发说明（4）：Celery 异步任务 & 定时任务
* 开发说明（5）：WebSocket 接口
* 开发说明（6）：Pytest 单测

![fastapi-common-tmpl.png](docs%2Ffastapi-common-tmpl.png)

#### 1. 技术栈

* Python：3.11.7+；
* FastAPI： 构建 API Web 框架；
* Tortoise-ORM：Asyncio ORM （对象关系映射器）库；
* Celery：分布式任务队列，异步任务/定时任务;
* Websocket：客户端和 服务器之间的持久性连接，提供双向、 全双工通信;
* Redis：分布式锁、缓存；
* PostgreSQL：数据库；

#### 2. 项目结构

```Linux
$ tree -L 5
.
├── app
│ ├── api                           # Demo：Restful api 接口
│ │ └── v1
│ │     ├── api.py                  # Demo：路由注册
│ │     ├── endpoints
│ │     │ ├── groups.py             # Demo：Group CRUD 接口示例
│ │     │ ├── others.py             # Demo：Redis、Websocket、WS 接口示例
│ │     │ ├── users.py              # Demo：User CRUD 接口示例
│ │     │ └── websockets.py         # Demo：Websocket 接口示例
│ ├── config.py                     # Demo：App Config 配置
│ ├── core
│ │ ├── celery_config.py            # Demo：Celery Config 配置
│ │ ├── celery.py                   # Demo：Celery App 入口
│ │ ├── logger.py                   # Demo：Log 工作库
│ │ ├── redis.py                    # Demo：Redis 工作库
│ │ ├── utils.py                    # Demo：通用工具库
│ │ └── websockets.py               # Demo：基础类及自定义 Websocket
│ ├── main.py                       # Demo：App入口及内置健康检查 API
│ ├── models
│ │ ├── base.py                     # Demo：基础数据模型
│ │ └── examples.py                 # Demo：数据模型（User、Group）
│ ├── schemas
│ │ └── examples.py                 # Demo：定义数据模型 Pydantic 模式（schemas），用于在应用程序中进行数据验证和序列化/反序列化
│ ├── services
│ │ └── examples.py                 # Demo：Services 层示例
│ └── tasks
│     ├── scheduler_tasks.py        # Celery 定时任务
│     └── tasks.py                  # Celery 异步任务
├── docs                            # 开发说明
├── deploy
│ └── docker-compose
│     ├── docker-compose.yml        # docker-compose 部署 yaml 文件 
│     └── env.template              # 环境变量配置
├── Dockerfile                      # 构建容器镜像
├── LICENSE                         # LICENSE 授权
├── migrations                      # 迁移文件
├── pyproject.toml                  # 项目管理
├── README.md                       # 项目说明
├── requirements.txt                # Demo 依赖项
└── tests                           # 单侧用例
```

#### 3. 项目配置

`cp ./deploy/docker-compose/env.template ./deploy/docker-compose/.env`

```
BACKEND_IMAGE=$IMAGE             # 部署镜像
DEBUG=false

# postgres 数据库配置
POSTGRES_HOST=example-postgres   # PostgreSQL 访问地址，默认是容器名称
POSTGRES_PORT=5432               # PostgreSQL 端口，默认 5432
POSTGRES_USER=example             # PostgreSQL 访问用户
POSTGRES_PASSWORD=example123       # PostgreSQL 访问密码
POSTGRES_DB=example              # PostgreSQL 访问数据库
DB_POOL_MAX=100                  # PostgreSQL 最大连接数
DB_POOL_CONN_LIFE=-1

# redis配置
REDIS_HOST=example-redis         # Redis 访问地址，默认是容器名称
REDIS_PORT=6379                  # Redis 端口，默认 6379
REDIS_USER=                      # Redis 访问用户
REDIS_PWD=                       # Redis 访问密码
```

#### 4. Migrations 数据库迁移

Aerich 是 TortoiseORM 的数据库迁移工具。当前 Demo 示例，会通过 example-migrations 容器完成数据迁移及初始化工作。若有自定义可参考如下命令操作；

**（1）初始化：**

执行 aerich 初始化：aerich init -t 指定配置，项目初始阶段执行;

```
aerich init -t config.TORTOISE_ORM
```

将会在目录下生成空的 migrations 文件夹和 pyproject.toml 文件

**（2）初始化数据库**

将模型映射到数据库中:

```
aerich init-db
```
此时数据库中就会生成对应的表。

**（3）【日常命令】更新模型迁移文件**

更新数据模型后，重新生成SQL迁移文件。
```
aerich migrate
```

**（4）【日常命令】升级到最新版本**

执行迁移文件更新数据库：

```
aerich upgrade

或

aerich upgrade xxxxx.py
```

**（5）【日常命令】降级到指定版本**

数据库回滚到指定版本：

```
aerich downgrade

或

aerich downgrade xxxxx.py
```

**（6）【日常命令】查看历史迁移记录**

```commandline
aerich history
```

**（7）【日常命令】显示迁移的 heads**

```commandline
aerich heads
```

#### 5. Docker 部署

下载代码，例：`git clone xxxx.xxx.xxx`

**（1）构建镜像**

```
# 进入 Demo 根目录
cd ./fastapi-common-tmpl

# 构建镜像 1.0
docker build -t fastapi-common-tmpl:1.0 .

# 检查镜像
docker images | grep fastapi-common-tmpl
```

**（2）env 环境变量配置**

修改环境变量: `mv ./deploy/docker-compose/env.template ./deploy/docker-compose/.env`

```text
# 指定 Demo 部署版本
BACKEND_IMAGE=fastapi-common-tmpl:1.0

# 数据库配置
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_USER=example
POSTGRES_PASSWORD=example123
POSTGRES_DB=example
DB_POOL_MAX=100
DB_POOL_CONN_LIFE=-1

# Redis 配置
REDIS_HOST=redis
REDIS_PORT=6379
```

**（3）docker-compose 部署**

根据需要修改：volumes 挂载点

```text

vi ./deploy/docker-compose/docker-compose.yml

...
volumes:
  example-data-postgres:
    name: example-data-postgres
    driver: local
    driver_opts:
      o: bind
      type: none
      # 自定义 Host 挂载点
      device: /data/example/postgres
  example-data-redis:
    name: example-data-redis
    driver: local
    driver_opts:
      o: bind
      type: none
      # 自定义 Host 挂载点
      device: /data/example/redis
```

例如：

```commandline
sudo mkdir /data/example/postgres
sudo mkdir /data/example/redis
```

启动：

```commandline
docker-compose -f ./deploy/docker-compose/docker-compose.yml up -d
```

关闭：

```commandline
docker-compose -f ./deploy/docker-compose/docker-compose.yml down
```

检查服务状态：

```
linux@jpzhang-dev:~/workspace/fastapi-common-tmpl$ docker ps -a

CONTAINER ID   IMAGE                   COMMAND                   CREATED         STATUS                            PORTS                                       NAMES
e0472333beb8   fastapi-common-tmpl:1.5   "celery -A app.core.…"   5 seconds ago   Up 3 seconds                                                                  example-celery
e5e97d5cb8c9   fastapi-common-tmpl:1.5   "celery -A app.core.…"   5 seconds ago   Up 3 seconds                                                                  example-scheduler
f978ad857466   fastapi-common-tmpl:1.5   "uvicorn app.main:ap…"   5 seconds ago   Up 3 seconds                      0.0.0.0:9000->9000/tcp, :::9000->9000/tcp   example-backend
dc241da98f18   fastapi-common-tmpl:1.5   "python init_data.py"     5 seconds ago   Exited (0) 2 seconds ago                                                      example-migrations
a72f7811771b   postgres:14.13          "docker-entrypoint.s…"   5 seconds ago   Up 4 seconds (health: starting)   0.0.0.0:5432->5432/tcp, :::5432->5432/tcp   example-postgres
430276b3216c   redis:7.0.15            "docker-entrypoint.s…"   5 seconds ago   Up 4 seconds (healthy)            0.0.0.0:6379->6379/tcp, :::6379->6379/tcp   example-redis

```

**服务介绍：**

- example-celery:  Celery 异步任务服务；  
- example-scheduler:  Celery 定时任务服务；  
- example-backend:  示例 Demo API 服务；   
- example-migrations:  数据库迁移及数据初始化服务，仅运行一次；  
- example-postgres:  PostgreSQL 服务；  
- example-redis:  Redis 服务；  

**（4）Demo Swagger UI**

访问地址：`http://<HOST IP>:9000/docs/`

