import inspect
import pkgutil
import importlib
from functools import wraps
from pathlib import Path

# 存储被 @Test_data 标记的变量或方法
TEST_DATA_REGISTRY = {}


# 定义 @Test_data 装饰器
def Test_data(obj):
    """装饰器，用于标记变量和方法"""
    if inspect.isfunction(obj):  # 如果是方法
        @wraps(obj)
        def wrapper(*args, **kwargs):
            return obj(*args, **kwargs)

        TEST_DATA_REGISTRY[obj.__name__] = obj()  # 直接存储方法名和返回值
        return wrapper
    else:  # 如果是变量
        TEST_DATA_REGISTRY[obj.__name__] = obj
        return obj


# 获取所有 @Test_data 标记的变量和方法
def get_test_data():
    """获取所有 @Test_data 变量 & 方法"""
    return TEST_DATA_REGISTRY


def load_test_data_from_path(config_path: Path):
    """
    遍历指定路径下的 Python 文件，动态导入并加载 @Test_data 变量
    :param config_path: 配置文件所在目录（Path 对象）
    """
    global TEST_DATA_REGISTRY
    config_path = Path(config_path)  # 确保是 Path 对象
    if not config_path.is_dir():
        raise ValueError(f"路径 {config_path} 不是一个有效的目录！")

    for file in config_path.glob("*.py"):  # 遍历所有 .py 文件0
        if file.name == "__init__.py":
            continue  # 跳过 __init__.py
        module_name = file.stem  # 获取不带 .py 的文件名
        spec = importlib.util.spec_from_file_location(module_name, file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # 动态加载模块