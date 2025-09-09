import os
from dataclasses import dataclass




def get_env_params(key):
    """
    Get params from system path.
    """
    v = os.environ.get(key)
    if not v:
        raise EnvironmentError(f"环境变量{key}未设置或为空，请确保它已正确配置。")
    return v

# 测试执行的home目录：$PROBE_HOME
PROBE_HOME = get_env_params("PROBE_HOME")