import json
import os
from pathlib import Path
from swagger_parser import SwaggerParser
from probeX.framework.utils.log import test_logger as logger
from probeX.framework.utils.SwaggerParse import convert_swagger_file
from probeX.framework.config.env import PROBE_HOME
from probeX.framework.config.Config import config


AIRS_HOME = Path(PROBE_HOME)
__SWAGGER_JSON_DIR = Path(config.swagger_doc_dir)


class Request_Params():
    def __init__(self, name, where, required, type, schema=None, description=None):
        self.name = name
        self.where = where
        self.required = required
        self.type = type
        self.schema = schema
        self.description = description


class Response_Params():
    def __init__(self, name, where, required, type, schema=None, description=None):
        self.name = name
        self.where = where
        self.required = required
        self.type = type
        self.schema = schema
        self.description = description
        

class AirsAPI:

    def __init__(self, path, method, id, parameters=None, summary=None, response=None):
        """
        Interface structure of Airs.
        Args:
            path:
            method:
            operationId:
            parameters:
            summary:
            response:
        Return:
            obj
        """
        self.path = path
        self.method = method,
        self.summary = summary,
        self.id = id,
        self.parameters = parameters,
        self.response = response


class AirsAPIEncoder(json.JSONEncoder):
    def default(self, o):
        return o.__dict__  


def gen_params(api_params:list, all_params:dict):
    for i in range(len(api_params)):
        param = api_params[i]
        if "schema" in param.keys():
            if "$ref" in param["schema"].keys():
                ref_name = param["schema"]["$ref"].split("/")[-1]
                api_params[i]["schema"] = all_params[ref_name]
    return api_params


def gen_response(api_response:dict, all_params:dict):
    for response_key, response_value in api_response.items():
        if "schema" in response_value.keys():
            if "$ref" in response_value["schema"].keys():
                ref_name = response_value["schema"]["$ref"].split("/")[-1]
                api_response[response_key]["schema"] = all_params[ref_name]
    return api_response


def parse_swagger_definition(swagger_file_path:str):
    convert_swagger_file(swagger_file_path)


def parse_swagger_json(swagger_json_file):
    apis = {}
    parse = SwaggerParser(swagger_json_file)
    for path, path_info in parse.specification["paths"].items():
        """
        path:
        """
        for method, api_detail in path_info.items():
            apis[api_detail["operationId"]] = AirsAPI(
                path=path,
                method=method,
                id=api_detail["operationId"],
                parameters=api_detail["parameters"],
                summary=api_detail["summary"] if "summary" in api_detail.keys() else "",
                response=api_detail["response"] if "response" in api_detail.keys() else {}
            )
    return apis


def all_airs_api():
    # 指定目录路径
    all_apis = {}
    swagger_output_dir = AIRS_HOME.joinpath("api", "swagger_output")
    if not os.path.exists(swagger_output_dir):
        os.makedirs(swagger_output_dir)
    for root, dirs, files in os.walk(__SWAGGER_JSON_DIR):
        for file in files:
            if file.endswith('.json'):
                swagger_file_path = os.path.join(root, file)
                swagger_output_path = os.path.join(swagger_output_dir, file)
                convert_swagger_file(swagger_file_path, swagger_output_path)
    # 遍历目录下所有文件, 转换swagger格式
    for root, dirs, files in os.walk(swagger_output_dir):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                all_apis.update(parse_swagger_json(file_path))
    return all_apis


if __name__ == '__main__':
    print(all_airs_api())
    