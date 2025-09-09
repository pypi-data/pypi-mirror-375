import pytest
import os
import inspect
from pathlib import Path
from probeX.framework.config.env import PROBE_HOME
from probeX.framework.config.Config import config
from probeX.framework.utils.reporter import Reporter
from probeX.framework.utils.log import test_logger as logger
from probeX.framework.utils.test_data_loader import load_test_data_from_path
from probeX.framework.utils.test_data_loader import TEST_DATA_REGISTRY

_CASE_HOME = Path(PROBE_HOME).joinpath("cases")


class TestDataStore:
    def __init__(self):
        self.data = {}

    def set(self, key, value):
        self.data[key] = value

    def get(self, key, default=None):
        return self.data.get(key, default)

    def delete(self, key):
        if key in self.data:
            del self.data[key]

    def clear(self):
        self.data.clear()


def load_variables_from_py_files():
    """
    加载指定目录下所有 Python 文件中定义的变量，并存入字典。
    :return: 包含所有变量的字典
    """
    result_dict = {}
    # 获取指定目录下所有 .py 文件
    py_files = Path(config.test_data_dir).glob("*.py")
    for py_file in py_files:
        try:
            file_content = py_file.read_text(encoding="utf-8")  # 读取文件内容
        except Exception as e:
            logger.error(f"无法读取 {py_file}: {e}")
            continue
        # 创建一个独立的命名空间
        local_vars = {}
        try:
            exec(file_content, {}, local_vars)  # 在隔离作用域执行代码
        except Exception as e:
            logger.error(f"加载文件 {py_file} 失败: {e}")
            continue
            # 过滤掉函数、类、对象，只保留普通变量
        filtered_vars = {
            k: v for k, v in local_vars.items()
            if not k.startswith("_") and not inspect.isfunction(v) and not inspect.isclass(v)
        }
        # 合并到结果字典
        result_dict.update(filtered_vars)
    return result_dict


class ProbeXPlugin:
    """
    pytest plugin for executing test cases.
    """

    def __init__(self):
        # 初始化全局测试数据存储
        load_test_data_from_path(config.test_data_dir)
        self.test_data_store = TEST_DATA_REGISTRY

    def pytest_configure(self, config):
        """在 pytest 启动时初始化测试数据"""
        config.test_data_store = self.test_data_store  # 将数据存储绑定到 pytest 配置对象
        logger.info("[ProbeXPlugin] Test data initialized.")

    def pytest_generate_tests(self, metafunc):
        """自动为测试方法注入 test_data 形参"""
        if "test_data" in metafunc.fixturenames:
            metafunc.parametrize("test_data", [metafunc.config.test_data_store])

    def pytest_sessionfinish(self, session, exitstatus):
        """在 pytest 结束时清理测试数据"""
        session.config.test_data_store.clear()
        logger.info("[ProbeXPlugin] Test data cleared.")


class CaseExecutor:

    def __init__(self, case, reporter: Reporter, task_name):
        self.case = case
        self.reporter = reporter
        self.task_name = task_name

    def execute(self, args):
        test_case = _CASE_HOME.joinpath(self.case)
        report_file = self.reporter.report_path.joinpath(f"{self.task_name}.html")
        ret_code = pytest.main(["-qq", test_case, f"--html={report_file}"], plugins=[ProbeXPlugin()])
        print(ret_code)