import shutil
from pathlib import Path
from probeX.framework.config.Config import config
from probeX.framework.config.env import PROBE_HOME
from probeX.framework.utils.log import test_logger as logger
from probeX.framework.entity.AirsAPI import all_airs_api


class SwaggerService:
    def __init__(self):
        pass

    def parse_swagger(self):
        if not config.swagger_doc_dir.exists():
            raise FileNotFoundError("Swagger doc dir not found. Please check config file.")
        # 获取所有 .json 文件
        # json_files = list(config.swagger_doc_dir.glob("*.json"))
        # 拷贝文件
        # 确保目标目录存在
        # config.swagger_api_dir.mkdir(parents=True, exist_ok=True)
        # for file in json_files:
            # shutil.copy(file, config.swagger_api_dir)
            # logger.debug(f"Copied: {file} -> {config.swagger_api_dir}")
        all_airs_api()

