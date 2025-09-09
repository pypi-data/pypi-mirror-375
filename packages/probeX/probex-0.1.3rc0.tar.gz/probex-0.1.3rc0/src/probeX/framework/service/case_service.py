from probeX.framework.schedule.case_schedule import CaseFlowConfig
from probeX.framework.schedule.case_schedule import CaseFlow
from probeX.framework.utils.log import test_logger as logger
from probeX.framework.config.Config import config

class CaseService:

    _TEST_FLOW_DIR = config.test_flow_dir

    def __init__(self):
        pass

    def execute_case(self, case_file: str):
        case_file_path = self._TEST_FLOW_DIR.joinpath(case_file)
        if not case_file_path.exists():
            raise FileNotFoundError(f"Test flow file {case_file_path} not found.")
        flowconfig = CaseFlowConfig(file_path=case_file_path).get_config()
        f = CaseFlow(case_file.split(".")[0])
        fun = f.create(flowconfig)
        fun()