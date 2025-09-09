#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: yanggyc
@created: 2024/5/23 14:12
@description:
"""
import time

from probeX.framework.client.HTTPClient import HttpClient
from probeX.framework.utils.log import test_logger as logger


class BaseModel(object):
    """
    Base Model
    """
    _get_list_key = "items"
    _get_id_key = "id"
    _get_name_key = "name"

    _Page_Info = {
        "page": 1,
        "pageSize": 10000,
        "sort": "",
        "order": ""
    }

    def __init__(self, name=None):
        """base init"""
        self.name = name
        self._id = None

    @property
    def client(self):
        return HttpClient(token=self.token, context=self.user_context)

    @property
    def id(self):
        """get id. """
        if self._id == None:
            if self.name and callable(self.get_id_by_name):
                self._id = self.get_id_by_name()
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    def get_id_by_name(self):
        list_res = self.list()
        for i in list_res[self._get_list_key]:
            if i[self._get_name_key] == self.name:
                return i[self._get_id_key]
        logger.warning("Not found item by name. Get id failed")

    def list(self):
        pass

    def detail(self):
        pass

    def wait_status(self, rounds, excepted_status, times=15):
        """
        Args:
            rounds: 等待轮数
            excepted_status: 期望状态
            times: 每次等待时间
        Returns:
            success: True
            fail: False
        """
        if isinstance(excepted_status, str):
            excepted_status = [excepted_status]
        for i in range(rounds):
            status = self.get_status()
            if status in excepted_status:
                logger.info("Wait for {time} seconds. The current status of the task is {c_status}, and the expected "
                            "status is {e_status}.".format(
                    time=i*times, c_status=status, e_status=excepted_status
                ))
                return
            else:
                time.sleep(times)
                logger.info("Wait for {time} seconds.The current status of the task is {c_status}, but the expected "
                            "status is {e_status}.".format(
                    time=i * times, c_status=status, e_status=excepted_status
                ))
                continue
        logger.error("Timeout.The expected status is  {c_status},But current status of the task is {e_status}.".format(
                    c_status=status, e_status=excepted_status))
        raise RuntimeError("Timeout.The expected status is  {e_status},But current status of the task is {c_status}.".format(
                    c_status=status, e_status=excepted_status))

    def get_status(self):
        """基类对获取状态方法不做实现."""
        logger.error("Please implement get_status")
        return ""
