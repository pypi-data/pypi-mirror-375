#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@File    :   environment.py
@Time    :   2025/04/27 16:55:33
@Author  :   yanggy 
@Version :   1.0
@Contact :   yangguangyu_cn@163.com
@License :   (C)Copyright 2021-2022, Liugroup-NLPR-CASIA
@Desc    :   None
'''
from probeX.framework.config.Config import config


class environment():
    """
    测试环境配置.
    """

    def __init__(self, environment_config_dict: dict):
        """
        environment_config_dict
        """
        for k, v in environment_config_dict.items():
            setattr(self, k, v)


def get_env_config():
    ""
    from probeX.framework.config.Config import config
    envs_config = config.get("env")
    for env_config in envs_config:
        if env_config.get("default", None):
            return environment(environment_config_dict=env_config)


env_config = get_env_config()
