from celery import Celery

# ========================================
# 说明: Celery App
# ========================================

app = Celery("ExampleCelery")
app.config_from_object('app.core.celery_config')
app.autodiscover_tasks(['app.tasks.tasks', 'app.tasks.scheduler_tasks'])


@app.task
def do_health_check():
    """
    # 内置：TODO 健康检查
    """
    print('健康检查: Celery 健康检查正常！')
