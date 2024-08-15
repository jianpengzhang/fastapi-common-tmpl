import logging

from app import settings

# ========================================
# 说明: 日志关联配置
# ========================================

logger = logging.getLogger()
logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
ch = logging.StreamHandler()
formatter = logging.Formatter(
    "%(asctime)s - %(process)d - %(module)s - %(funcName)s - line:%(lineno)d - %(levelname)s - %(message)s"
)

ch.setFormatter(formatter)
logger.addHandler(ch)

LOG = logger
