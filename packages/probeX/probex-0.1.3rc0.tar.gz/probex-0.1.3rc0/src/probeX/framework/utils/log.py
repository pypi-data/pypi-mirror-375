import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from probeX.framework.config.env import PROBE_HOME
from probeX.framework.config.Config import config


LOG_DIR = Path(PROBE_HOME).joinpath("logs")
os.makedirs(LOG_DIR, exist_ok=True)  # 确保日志目录存在

# 获取日志级别
LOG_LEVEL = config.get("log_level")


def setup_logger(name, log_file, level=LOG_LEVEL):
    """配置日志"""
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s")

    handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=10, encoding="utf-8")
    handler.setFormatter(formatter)
    handler.setLevel(level)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


# 配置不同模块日志
web_logger = setup_logger("web", os.path.join(LOG_DIR, "web.log"))
test_logger = setup_logger("test_runner", os.path.join(LOG_DIR, "test_runner.log"))

# 测试日志输出
web_logger.info("Web 服务启动")
test_logger.debug("测试用例执行")