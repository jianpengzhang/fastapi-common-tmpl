import asyncio
import threading

from app import settings


# ========================================
# 说明: 通用工具库
# ========================================

def run_celery_task(task, *args, **kwargs):
    # kwargs里的eta和expires参数用于celery，其他参数用于task
    eta = kwargs.pop("eta", None)
    expires = kwargs.pop("expires", None)
    if settings.TEST:
        return task(*args, **kwargs)
    return task.apply_async(args, kwargs, eta=eta, expires=expires)


class SingletonMeta(type):
    """
    单例元类
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        方法重载，确保每次创建类的实例时，返回同一个实例;
        _instances，字典用于存储已经创建的实例
        :param args:
        :param kwargs:
        :return:
        """
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class AsyncLoopCreator:
    """
    创建单独的线程并运行一个独立的事件循环；

    创建事件循环：确保在程序中只有一个事件循环实例。
    线程安全：通过线程锁防止 race condition，确保事件循环的创建和访问是线程安全的。
    独立运行：事件循环在单独的守护线程中运行，确保主线程的退出不会影响事件循环的运行。
    多线程环境中，尤其是在使用 Celery 等非异步框架的环境中，异步代码可以正常运行而不会遇到事件循环关闭的错误 (RuntimeError: Event loop is closed)。
    """
    loop = None

    @classmethod
    def get_loop(cls):
        if cls.loop is None:
            with threading.Lock():
                if not cls.loop:
                    # 创建事件循环
                    cls.loop = asyncio.new_event_loop()
                    # 创建线程运行事件循环:target 指定线程运行函数，args 指定传递标函数参数
                    thread = threading.Thread(target=cls.run_event_loop, args=(cls.loop,))
                    # 守护线程:主线程退出，该线程自动退出
                    thread.daemon = True
                    # 启动线程，运行 run_event_loop 方法
                    thread.start()
                return cls.loop
        return cls.loop

    @staticmethod
    def run_event_loop(loop):
        # 设置当前线程的事件循环为传递进来的 loop
        asyncio.set_event_loop(loop)
        try:
            # 运行事件循环，直到调用 loop.stop() 停止它
            loop.run_forever()
        finally:
            # 确保事件循环能被正确关闭。
            loop.close()
