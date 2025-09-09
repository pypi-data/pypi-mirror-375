#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: yanggyc
@created: 2024/5/23 11:07
@description: 
"""
import requests
import json
from pathlib import Path
from probeX.framework.utils.log import test_logger as logger
from probeX.framework.config.Config import config
from probeX.framework.config.environment import env_config
from probeX.framework.utils.ApiConfigLoader import ApiConfigLoader
from probeX.framework.entity.AirsAPI import all_airs_api as airs_api


class HttpClient:

    _ALL_AIRS_API = airs_api()

    def __init__(self, timeout=30):
        self.base_url = env_config.host
        self.timeout = timeout
        self.session = requests.Session()
        self._headers = {}

    def _full_url(self, url):
        """gen url"""
        return self.base_url + url

    @property
    def headers(self):
        """初始headers"""
        return self._headers

    @headers.setter
    def headers(self, headers):
        self._headers = headers

    def add_header(self, header):
        if self.headers is not {}:
            self._headers = {**self.headers, **header}
        else:
            self._headers = header

    @property
    def api_config_loader(self):
        return ApiConfigLoader(Path.joinpath(config.airs_home, "data", "api"))

    def request_yaml_api(self, api_name, expect_success=True, **kwargs):
        api_info = self.api_config_loader.get_api_config(api_name=api_name)
        # url 参数化
        full_url = self._full_url(api_info["url"])
        full_url = full_url.format(**kwargs)
        # header参数化
        headers = api_info["headers"] if "headers" in api_info.keys() else {}
        headers = {**self.headers, **headers} if headers is not None else self.headers
        # 替换header中的动态参数
        for key in headers.keys():
            if isinstance(headers[key], str) and '{' in headers[key] and '}' in headers[key]:
                headers[key] = headers[key].format(**kwargs)
        body = api_info["body"] if "body" in api_info.keys() else {}

        # 递归替换body中的动态参数
        def recursive_format(infos):
            # 遍历字典
            temp_type = type(infos)
            temp = temp_type()

            if isinstance(infos, dict):
                for info_key, info_value in infos.items():
                    if isinstance(info_value, dict) or isinstance(info_value, list):
                        temp[info_key] = recursive_format(info_value)
                    elif isinstance(info_value, str):
                        if '{' in info_value and '}' in info_value:
                            # 截取变量名 - v
                            v = info_value[1:-1:]
                            # 参数为str时，采用.format，可用于字符串拼接
                            if isinstance(kwargs[v], str):
                                temp[info_key] = info_value.format(**kwargs)
                            # 其他情况直接赋值
                            else:
                                temp[info_key] = kwargs[v]
                        # 不需要替换的参数，原样传回
                        else:
                            temp[info_key] = info_value
                    else:
                        temp[info_key] = info_value
            elif isinstance(infos, list):
                for i in range(len(infos)):
                    if isinstance(infos[i], dict) or isinstance(infos[i], list):
                        temp.insert(i, recursive_format(infos[i]))
                    else:
                        temp.insert(i, infos[i])
            else:
                raise RuntimeError(f"Parse json file error, content is {infos}")
            return temp

        body = recursive_format(body)
        method = api_info["method"] if "method" in api_info.keys() else "POST"
        return self.send_request(full_url=full_url,
                                 method=method,
                                 body=body,
                                 headers=headers,
                                 expect_success=expect_success,
                                 **kwargs)

    def request_swagger_apis(self, api_name, expect_success=True, **kwargs):
        try:
            # if "clusterId" not in kwargs.keys():
            #     kwargs["clusterId"] = self.cluster_id
            # if "zoneId" not in kwargs.keys():
            #     kwargs["zoneId"] = self.zone_id
            api = self._ALL_AIRS_API[api_name]
            path = "/preStr" + api.path
            method = api.method[0]
            summary = api.summary
            api_id = api.id
            params = api.parameters
            response = api.response
            full_url = self._full_url(path).format(**kwargs)
            body = generate_body_from_swagger_params(params[0], **kwargs)
            params = generate_params_from_swagger_params(api.path, params[0], **kwargs)
            return self.send_request(full_url=full_url,
                                     method=method,
                                     body=body,
                                     params=params,
                                     headers=self.headers,
                                     expect_success=expect_success,
                                     **kwargs)
        except KeyError:
            raise RuntimeError(f"No swagger api {api_name} found")

    def send_request(self, full_url, body, headers, method, expect_success, params, **kwargs):
        """Send Http Request.

        Args:
            full_url (_type_): _description_
            body (_type_): _description_
            headers (_type_): _description_
            method (_type_): _description_
            expect_success (_type_): _description_
            params (_type_): _description_

        Returns:
            _type_: _description_
        """
        logger.debug("--------********--------HTTP REQUEST STSRT--------********--------")
        logger.debug(f"Request {full_url} with body={body} and headers={headers}")
        try:
            response = self.session.request(url=full_url, method=method, json=body, headers=headers,
                                            params=params, timeout=self.timeout)
            logger.debug(f"Received response with status code: {response.status_code}")
            logger.debug(f"Response content: {response.content}")
            if expect_success:
                response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(f"Request request failed: {e}")
            logger.error(f"Received response with status code: {response.status_code}")
            logger.error(f"Request {full_url} with body={json.dumps(body)} and headers={headers}. \
                                        Response content: {response.content}")
        finally:
            logger.debug("--------********--------HTTP REQUEST END--------********--------")
            return response


def generate_value(data_type, key=None):
    """
    根据类型生成值或从参考字典中获取值。
    """
    # 根据类型生成值
    if data_type == "string":
        return ""
    elif data_type == "integer":
        return 0
    elif data_type == "boolean":
        return True
    elif data_type == "list":
        return []
    elif data_type == "object":
        return {}
    # 其他类型
    return None


def recursive_parse(dictionary, **kwargs):
    result = {}
    for key, value in dictionary.items():
        if key in kwargs.keys():
            result[key] = kwargs[key]
        elif isinstance(value, dict) and "properties" in value and key not in kwargs.keys():
            # 如果包含properties，则递归调用
            result[key] = recursive_parse(value["properties"], **kwargs)
        elif isinstance(value, dict) and "type" in value:
            # 根据类型生成值
            result[key] = generate_value(value["type"], key)
        else:
            result[key] = value
    return result


def generate_body_from_swagger_params(params:dict, **kwargs)->dict:
    body = {}
    for param in params:
        if param["in"] == "body":
            if "schema" in param.keys() and "properties" in param["schema"].keys():
                body = recursive_parse(param["schema"]["properties"], **kwargs)
                if "header" in body.keys():
                    body.pop("header")
    return body


def generate_params_from_swagger_params(path, params:dict, **kwargs)->dict:
    p = {}
    for param in params:
        if param["in"] == "path" and "{"+param["name"]+"}" not in path:
            p[param["name"]] = kwargs.get(param["name"])
    return p


# def parse_all_apis_params_struct():
#     client = HttpClient()
#     apis = client._ALL_AIRS_API
#     api_params = {}
#     for api_key, api_info in apis.items():
#         api_params[api_key] = generate_body_from_swagger_params(api_info.parameters[0])
#
#     body_struct_file = AIRS_API_HOME.joinpath("api_struct.json")
#     with open(body_struct_file, mode="w", encoding="utf-8") as f:
#         f.write(json.dumps(api_params, indent=4))


if __name__ == "__main__":
    pass