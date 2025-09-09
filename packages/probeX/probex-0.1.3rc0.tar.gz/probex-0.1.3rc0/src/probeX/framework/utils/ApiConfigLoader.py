#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: yanggyc
@created: 2024/5/23 17:59
@description:
"""
import os
import json
import yaml
import configparser
import importlib.util
import requests


class ApiConfigLoader:
    def __init__(self, config_folder):
        self.config_folder = config_folder
        self.api_configs = self._load_api_configs()

    def _load_api_configs(self):
        api_configs = {}
        for filename in os.listdir(self.config_folder):
            if filename.endswith('.json'):
                api_configs.update(self._load_json_config(os.path.join(self.config_folder, filename)))
        return api_configs

    def _load_json_config(self, filepath):
        with open(filepath, 'r') as file:
            return json.load(file)

    def get_api_config(self, api_name):
        if self.api_configs is None:
            self.api_configs = self._load_api_configs()
        if api_name not in self.api_configs:
            raise ValueError(f"API configuration for {api_name} not found")
        return self.api_configs[api_name]

    def send_request(self, api_name, dynamic_params):
        if api_name not in self.api_configs:
            raise ValueError(f"API configuration for {api_name} not found")

        api_info = self.api_configs[api_name]
        url = api_info['url']
        method = api_info['method'].upper()
        headers = api_info.get('headers', {})
        body = api_info.get('body', {})

        # 替换URL中的动态参数
        url = url.format(**dynamic_params)

        # 替换body中的动态参数
        for key in body:
            if isinstance(body[key], str) and '{' in body[key] and '}' in body[key]:
                body[key] = body[key].format(**dynamic_params)

        response = None
        if method == 'GET':
            response = requests.get(url, headers=headers, params=dynamic_params)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=body)
        else:
            raise ValueError(f"HTTP method {method} not supported")

        return response


if __name__ == '__main__':
    config_folder = 'api_config'
    loader = ApiConfigLoader(config_folder)

    # 示例：发送GET请求
    dynamic_params = {'param1': 'value1', 'param2': 'value2'}
    response = loader.send_request('api1', dynamic_params)
    print(response.status_code, response.json())

    # 示例：发送POST请求
    dynamic_params = {'dynamic_key2': 'new_value2'}
    response = loader.send_request('api2', dynamic_params)
    print(response.status_code, response.json())
