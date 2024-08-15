# 开发说明（4）：Celery 异步任务 & 定时任务

## 1. 说明

下面是如何在 FastAPI Demo 项目中集成 Celery，实现定时任务和异步任务示例说明。

## 2. 安装依赖

安装 Celery 和用于与 Redis 或 RabbitMQ 交互的库（这里使用 Redis 作为消息代理）。

**requirements.txt 文件：** 新增依赖项：

```
celery==5.4.0
eventlet==0.36.1
flower==2.0.1(可选，监控和管理 Celery 集群)
```

* 激活 Demo Python 虚拟环境：`$ source fastapi-common-tmpl/bin/activate`  
* 安装依赖：`$ pip install -r requirements.txt`

## 3. 配置 Celery

在项目中创建 app/core/celery.py 文件，定义一个 Celery 应用程序实例，并配置了该实例的行为。

```
# app/core/celery.py

from celery import Celery

app = Celery("ExampleCelery")
app.config_from_object('app.core.celery_config')
app.autodiscover_tasks(['app.tasks.tasks', 'app.tasks.scheduler_tasks'])
```

**代码解释：**

* (1). 导入 Celery  
    `from celery import Celery`：Celery 是一个分布式任务队列，用于执行后台任务，这里从 Celery 包中导入了 Celery 类，以便创建一个 Celery 应用实例；
* (2). 创建 Celery 应用实例    
    `app = Celery("ExampleCelery")`：实例化，Celery("ExampleCelery") 创建了一个名为 "ExampleCelery" 的 Celery 应用实例，这个名字通常用于区分不同的 Celery 应用程序；
* (3). 配置 Celery  
    `app.config_from_object('app.core.celery_config')`：加载配置，config_from_object 方法从指定的配置对象或模块中加载 Celery 的配置选项。本例中，配置文件的位置是 'app.core.celery_config'，这通常是一个 Python 模块或对象，定义了 Celery 的各种配置选项，例如 broker_url、result_backend 等；
* (4). 自动发现任务  
    `app.autodiscover_tasks(['app.tasks.tasks', 'app.tasks.scheduler_tasks'])`：任务自动发现，autodiscover_tasks 方法会自动发现并加载指定模块中的任务。在这里，指定了两个模块 'app.tasks.tasks' 和 'app.tasks.scheduler_tasks'。Celery 会在这些模块中搜索并注册所有定义的任务（即带有 @celery.task 装饰器的函数）。  
     简化任务导入: 通过自动发现，可以避免在每个任务模块中手动导入任务到 Celery 应用中，提高了代码的可维护性和组织性。

## 4. 配置 Celery 设置

在项目中创建 app/core/celery_config.py 文件，加入 Celery 配置。

```
# app/core/celery_config.py

from celery.schedules import crontab
from app import settings

task_serializer = 'json'
accept_content = ['json']
result_serializer = 'json'
timezone = settings.TIMEZONE
broker_url = settings.BASE_REDIS + '1'
result_backend = settings.BASE_REDIS + '1'
task_default_queue = 'example'
```

**配置说明：**
    
* (1). 任务序列化设置  
    * `task_serializer`: 定义任务消息的序列化格式为 'json'，即在任务消息传递时使用 JSON 格式进行序列化;  
    * `accept_content`: 定义接受的内容类型为 'json'，限制 Celery 只接受 JSON 格式的消息;  
    * `result_serializer`: 定义任务结果的序列化格式为 'json'，即任务执行完毕后，结果会以 JSON 格式进行存储;

* (2). 时区设置  
    * `timezone`: 设置 Celery 时区，通常是一个字符串，如 'Asia/Shanghai'。时区信息从 settings.TIMEZONE 变量中获取，确保所有任务调度在相同的时区下进行。

* (3). 消息队列设置  
    * `broker_url`: 定义消息队列（broker）连接 URL，指定了 Celery 使用 Redis 作为消息队列，并连接到 Redis 数据库的第一个数据库 ('1');
                    settings.BASE_REDIS 通常包含 Redis 的基本连接信息，如 redis://localhost:6379/，加上 '1' 指定使用 Redis 的第一个数据库;
    * `result_backend`: 使用 Redis 作为结果后端;

* (4). 默认任务队列  
    * `task_default_queue`: 定义默认的任务队列名称为 'example'，如果没有为任务指定特定的队列，任务将被发送到这个默认队列；

## 5. 定义异步任务

在项目创建 app/tasks/tasks.py 文件，并在 tasks.py 文件中创建异步任务。

```
app/tasks/tasks.py

from app.core.celery import app


@app.task
def add(x: int, y: int) -> int:
    return x + y

@app.task
def mul(x: int, y: int) -> int:
    return x * y

@app.task
def sum_list(numbers: list) -> int:
    return sum(numbers)
```

**【扩展】** Celery中 @app.task与@shared_task 的区别  
`@app.task() 装饰器`：Celery 装饰器，用于将函数注册为 Celery 任务；    
`@shared_task() 装饰器`：Celery 装饰器，用于将函数注册为共享任务（shared task），共享任务是一种特殊类型的任务，可以跨多个Celery应用程序共享和调用，如果任务需要在多个 Celery 应用程序中共享，或者希望使用共享任务的特性，那么可以考虑使用此装饰器；

## 6. 在 FastAPI 中调用异步任务

在 app/api/v1/endpoints/ 中定义 API 端点，调用异步任务，可创建新的接口文件或在已有文件中加入如下代码：

```
# app/api/v1/endpoints/user.py

@user_router.post("/add-task/")
async def add_task(a: int, b: int):
    task = add.apply_async(args=[a, b])
    return {"task_id": task.id, "status": task.status}


@user_router.get("/task-result/{task_id}")
async def get_task_result(task_id: str):
    task_result = add.AsyncResult(task_id)
    if task_result.state == "PENDING":
        return {"status": task_result.state}
    elif task_result.state != "FAILURE":
        return {"status": task_result.state, "result": task_result.result}
    else:
        return {"status": task_result.state, "result": str(task_result.info)}    
```

## 7. 配置定时任务

在项目创建 app/tasks/scheduler_tasks.py 文件，并在 scheduler_tasks.py 文件中创建定时任务。

```
app/tasks/scheduler_tasks.py

import datetime

from celery import shared_task


@shared_task()
def get_current_time():
    """
    # TODO 示例：定时获取当前时间
    """
    print(f"TODO 示例：当前时间（周期任务）: {datetime.datetime.now().strftime('%Y-%m-%d  %H:%M:%S')}")
```

**配置周期性任务：**

Celery 配置文件 app/core/celery_config.py 加入周期性任务。

```
# 配置任务周期性
beat_schedule = {
    'get_current_time': {
        'task': 'app.tasks.scheduler_tasks.get_current_time',
        'schedule': crontab(minute='*/1'),  # Every minute
    },
}
```

`beat_schedule`: 定义 Celery Beat 任务调度，这里定义一个名为 'get_current_time' 周期性任务；  
`task`: 任务的完整路径，这里指向 'app.tasks.scheduler_tasks.get_current_time'，表示将执行 get_current_time 这个任务；    
`schedule`: 使用 crontab(minute='*/1') 来定义任务调度频率，minute='*/1' 表示每分钟执行一次该任务；  

## 8. 启动 Celery 和 Celery Beat

分别启动 Celery worker 和 Celery Beat：

```
# 启动 Celery Worker
celery -A app.core.celery worker -l INFO -c 1000 -P eventlet

# 启动 Celery Beat（用于定时任务）
celery -A app.core.celery beat -l info --schedule celerybeat-schedule.db
```

## 9. 使用 Flower 监控 Celery

Flower 是 Celery 的实时监控工具，可以用它来监控任务执行情况。

```
celery -A app.core.celery flower --port=5555
```

然后在浏览器中访问 http://localhost:5555 查看 Flower 的控制台。

## 10. 验证

**(1). 异步任务：**

通过访问 `http://<IP>:9001/docs` 查看自动生成的 API 文档，并通过其中的接口来测试异步任务功能。

示例新增接口：

* 两数相加：`POST  /api/v1/users/add-task/` 
    ```
    /api/v1/users/add-task/?a=1&b=1， 返回：
    {
      "task_id": "859b1fd1-0d0e-48a2-8a75-63c2ff7b5b57",
      "status": "PENDING"
    }
    ```
* 获取Task 任务结果 `GET /api/v1/users/task-result/{task_id}`
    ```
    /api/v1/users/task-result/859b1fd1-0d0e-48a2-8a75-63c2ff7b5b57， 返回：
    {
      "status": "SUCCESS",
      "result": 2
    }
    ```

**(2). 周期性任务：**

启动 Celery worker 和 Celery Beat 后，可观察控制台日志输出：

Celery Beat：

```
# 每隔一分钟调度
(fastapi-common-tmpl) ubuntu@jpzhang-dev:~/workspace/fastapi-common-tmpl$ celery -A app.core.celery beat -l info --schedule celerybeat-schedule.db
celery beat v5.4.0 (opalescent) is starting.
__    -    ... __   -        _
LocalTime -> 2024-08-14 16:04:10
Configuration ->
    . broker -> redis://127.0.0.1:6379/1
    . loader -> celery.loaders.app.AppLoader
    . scheduler -> celery.beat.PersistentScheduler
    . db -> celerybeat-schedule.db
    . logfile -> [stderr]@%INFO
    . maxinterval -> 5.00 minutes (300s)
[2024-08-14 16:04:10,153: INFO/MainProcess] beat: Starting...
[2024-08-14 16:04:10,166: INFO/MainProcess] Scheduler: Sending due task get_current_time (app.tasks.scheduler_tasks.get_current_time)
[2024-08-14 16:05:00,000: INFO/MainProcess] Scheduler: Sending due task get_current_time (app.tasks.scheduler_tasks.get_current_time)
[2024-08-14 16:06:00,000: INFO/MainProcess] Scheduler: Sending due task get_current_time (app.tasks.scheduler_tasks.get_current_time)
```

Celery worker：

```
# 每隔一分钟执行，打印日志
[2024-08-14 16:04:10,177: INFO/MainProcess] Task app.tasks.scheduler_tasks.get_current_time[6913d754-d3bb-42fd-b1d2-581c3b979cb9] received
[2024-08-14 16:04:10,178: WARNING/MainProcess] TODO 示例：当前时间（周期任务）: 2024-08-14  16:04:10
[2024-08-14 16:04:10,185: INFO/MainProcess] Task app.tasks.scheduler_tasks.get_current_time[6913d754-d3bb-42fd-b1d2-581c3b979cb9] succeeded in 0.007206028327345848s: None
[2024-08-14 16:05:00,006: INFO/MainProcess] Task app.tasks.scheduler_tasks.get_current_time[c041fc7e-9dd4-4151-8e0b-694429002580] received
[2024-08-14 16:05:00,007: WARNING/MainProcess] TODO 示例：当前时间（周期任务）: 2024-08-14  16:05:00
[2024-08-14 16:05:00,017: INFO/MainProcess] Task app.tasks.scheduler_tasks.get_current_time[c041fc7e-9dd4-4151-8e0b-694429002580] succeeded in 0.009737113490700722s: None
```

