from prefect import task, flow, get_run_logger
import yaml
from probeX.framework.utils.utils import get_now_time_str
from probeX.framework.utils.reporter import Reporter
from probeX.framework.schedule.executor import CaseExecutor


class CaseTask:

    def __init__(self, name, action, reporter: Reporter):
        self.name = name
        self.action = action
        self.reporter = reporter

    def create(self):
        @task(name=self.name, task_run_name=f"{self.name}-{get_now_time_str()}")
        def dynamic_task(*args):
            logger = get_run_logger()
            executor = CaseExecutor(case=self.action, reporter=self.reporter, task_name=self.name)
            executor.execute(args)
            logger.info(f"{self.name} executed with args: {args}")
            logger.info(f"reporter dir is {self.reporter.report_path}")
            logger.info(f"reporter url is {self.reporter.report_url}{self.name}.html")
            return f"{self.name} result"
        return dynamic_task


class CaseFlowConfig:
    def __init__(self, file_path):
        self.file_path = file_path

    def get_config(self):
        with open(self.file_path, 'r') as f:
            return yaml.safe_load(f)


class CaseFlow:

    def __init__(self, name):
        self.name = name
        self.params_context = None
        self._object_context = None

    @property
    def params_context(self):
        return self._params_context

    @params_context.setter
    def params_context(self, params_context):
        self._params_context = params_context

    def add_params_context(self, context_item):
        for k, v in context_item.items():
            self._params_context[k] = v

    @property
    def object_context(self):
        return self._object_context

    @object_context.setter
    def object_context(self, object_context):
        self._object_context = object_context

    def add_object_context(self, context_item):
        for k, v in context_item.items():
            self._object_context[k] = v

    def create(self, flow_config: CaseFlowConfig):
        @flow(name=self.name, flow_run_name=f"{self.name}-{get_now_time_str()}")
        def dynamic_flow(*args):
            task_map = {}  # 存储动态任务函数
            task_results = {}  # 存储任务执行结果
            reporter = Reporter(report_dir=f"report-{get_now_time_str()}")
            # **1. 解析 YAML 并创建任务**
            config = flow_config
            for task_info in config["tasks"]:
                task_name = task_info["name"]
                action = task_info["action"]

                # 动态生成任务函数
                case_task = CaseTask(task_name, action, reporter)
                task_func = case_task.create()
                task_map[task_name] = task_func  # 存储任务函数

            # **2. 执行任务，确保依赖顺序**
            for task_info in config["tasks"]:
                task_name = task_info["name"]
                params = task_info["params"]

                # 获取任务的所有依赖
                dependencies = config.get("dependencies", {}).get(task_name, [])

                # **确保任务的输入包含其依赖任务的结果**
                dep_results = [task_results[dep] for dep in dependencies]  # 获取依赖的结果
                task_results[task_name] = task_map[task_name](*dep_results, *params)  # 依赖优先执行

            # **3. 打印所有任务的结果**
            for task_name, result in task_results.items():
                print(f"{task_name} result: {result}")
        return dynamic_flow


if __name__ == '__main__':
    flowconfig = CaseFlowConfig(file_path="test_case.yaml").get_config()
    f = CaseFlow("testcase")
    fun = f.create(flowconfig)
    fun()


