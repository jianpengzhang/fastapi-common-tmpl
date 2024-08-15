from celery import shared_task


# ========================================
# 说明: Celery 异步任务
# ========================================

@shared_task()
def eg_task():
    """
    # TODO 示例：异步任务
    """
    print('TODO 示例：异步任务')
