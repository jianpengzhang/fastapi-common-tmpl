from celery.schedules import crontab

from app import settings

# ========================================
# 说明: Celery 配置文件
# ========================================

task_serializer = 'json'
accept_content = ['json']
result_serializer = 'json'
timezone = settings.TIMEZONE
broker_url = settings.BASE_REDIS + '1'
task_default_queue = 'example'

# 配置任务路由
# task_routes = {
#     'app.tasks.tasks*': {'queue': 'example'},
#     'app.tasks.schedule_tasks*': {'queue': 'scheduler'},
# }

# 配置任务周期性
beat_schedule = {
    'get_current_time': {
        'task': 'app.tasks.scheduler_tasks.get_current_time',
        'schedule': crontab(minute='*/1'),  # Every minute
    },
    'push_websocket_data': {
        'task': 'app.tasks.scheduler_tasks.push_websocket_data',
        'schedule': 5,
    },
}
