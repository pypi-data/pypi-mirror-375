#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: yanggyc
@created: 2024/5/23 14:26
@description: 
"""
import yaml
from pathlib import Path
from probeX.framework.config.env import PROBE_HOME


_CONFIG_FILE = Path(PROBE_HOME).joinpath('config', "probe_config.yaml")

class Config:
    """
    配置解析
    """
    def __init__(self, config_file=_CONFIG_FILE):
        self.config_file = config_file

    def parse_dict(self):
        """解析配置"""
        with open(self.config_file, 'r') as file:
            config = yaml.safe_load(file)
        return config

    def get(self, key, default=None):
        """
        Args:
            key: 配置信息key, 多层用 . 分隔, 数组用索引表示。如 users.1.name
            default: None
        Returns:
            config
        """
        if isinstance(key, str):
            keys = key.split('.')
            configs = self.parse_dict()
            for key in keys:
                if isinstance(configs, list):
                    try:
                        configs = configs[int(key)]
                    except ValueError:
                        raise RuntimeError("{key} should be int or str".format(key=key))
                    continue
                if key not in configs.keys():
                    from probeX.framework.utils.log import test_logger as logger
                    logger.warning(f"Not found {key} in config file".format(key=key))
                    return default
                else:
                    configs = configs[key]
            return configs
        else:
            raise TypeError('key must be str')

    @property
    def swagger_doc_dir(self):
        return Path(self.get("swagger_api_dir"))

    @property
    def swagger_api_dir(self):
        return Path(PROBE_HOME).joinpath("api", "swagger")

    @property
    def test_flow_dir(self):
        return Path(PROBE_HOME).joinpath("test_flow")

    @property
    def test_data_dir(self):
        return Path(PROBE_HOME).joinpath("data", "test_data")
    
    @property
    def test_report_dir(self):
        return Path(PROBE_HOME).joinpath("reports")


config = Config()
