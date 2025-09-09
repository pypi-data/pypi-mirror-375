import json
import copy
import sys

from probeX.framework.utils.log import test_logger as logger


def resolve_ref(schema, definitions):
    """递归解析并展开JSON中的$ref字段。"""
    if isinstance(schema, dict):
        # 如果包含$ref字段，则解析引用
        if '$ref' in schema:
            ref_path = schema['$ref'].split('/')
            if ref_path[1] == 'definitions' and ref_path[2] in definitions:
                # 复制引用的定义，避免修改原始数据
                resolved = copy.deepcopy(definitions[ref_path[2]])
                # 递归解析嵌套的$ref
                return resolve_ref(resolved, definitions)
            else:
                return schema  # 如果未找到引用，保持原样
        else:
            # 对嵌套字段递归解析
            return {k: resolve_ref(v, definitions) for k, v in schema.items()}
    elif isinstance(schema, list):
        return [resolve_ref(item, definitions) for item in schema]
    else:
        return schema

def expand_refs_in_paths(paths, definitions):
    """展开paths部分中的所有$ref引用。"""
    for path, methods in paths.items():
        for method, details in methods.items():
            if 'parameters' in details:
                details['parameters'] = resolve_ref(details['parameters'], definitions)
            if 'responses' in details:
                details['responses'] = resolve_ref(details['responses'], definitions)
    return paths

def expand_refs_in_definitions(swagger_data):
    """展开Swagger JSON中definitions部分的所有$ref引用。"""
    if 'definitions' not in swagger_data:
        return swagger_data  # 无definitions部分，直接返回

    # 解析并展开每个定义
    expanded_definitions = {}
    for name, definition in swagger_data['definitions'].items():
        expanded_definitions[name] = resolve_ref(definition, swagger_data['definitions'])

    # 将definitions替换为展开后的结构
    swagger_data['definitions'] = expanded_definitions
    return swagger_data

def convert_swagger_file(input_file, output_file):
    # 读取Swagger JSON文件
    with open(input_file, 'r', encoding='utf-8') as f:
        swagger_data = json.load(f)

    # 展开definitions中的$ref引用
    swagger_data = expand_refs_in_definitions(swagger_data)

    # 展开paths中的$ref引用
    if 'paths' in swagger_data:
        swagger_data['paths'] = expand_refs_in_paths(swagger_data['paths'], swagger_data['definitions'])

    # 保存展开后的JSON数据
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(swagger_data, f, ensure_ascii=False, indent=2)

    logger.debug(f"展开后的Swagger JSON文件已保存为: {output_file}")

