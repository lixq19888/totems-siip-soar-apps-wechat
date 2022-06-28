"""
app工具类，封装取参数和返回对象
"""

import json
import sys
from urllib.parse import unquote


def get_response_json(data, status='Success'):
    """
    返回数据给调用者
    :param data: data数据
    :param status: 默认是成功的，可以不传，失败需要传 Failure
    :return:
    """
    result = {'status': status, 'data': data}
    if isinstance(data, str):
        result['schema'] = {'type': 'STRING'}
    elif isinstance(data, int) or isinstance(data, float):
        result['schema'] = {'type': 'INTEGER'}
    elif isinstance(data, bool):
        result['schema'] = {'type': 'BOOLEAN'}
    elif isinstance(data, dict):
        result['schema'] = {'type': 'JSON_OBJECT'}
    elif isinstance(data, list):
        result['schema'] = {'type': 'JSON_ARRAY'}
    result = json.dumps(result)
    print(result)
    print("--------------------------------")
    if status == 'Failure':
        raise ValueError(data)
    return result


def get_param_value(param_item):
    """
    获取某项参数值
    :param param_item:
    :return: 具体值
    """
    if param_item is None:
        get_response_json('缺少参数', 'Failure')
        return
    val = param_item.get('value', '')
    if val == '':
        val = param_item.get('defaultValue')
    if param_item.get('required') and (val is None or val == ''):
        get_response_json(param_item.get('name') + '不能为空', 'Failure')
    val_type = param_item.get('schema')['type']
    if val_type == 'INTEGER':
        return int(val)
    elif val_type == 'BOOLEAN':
        return str(val).upper() == str('TRUE')
    elif val_type == 'STRING':
        return str(val)
    elif val_type == "JSON_OBJECT":
            return urllib.parse.unquote(str(val))
    return val


def get_input_param(app_name, input_data=None, action_select=None):
    """
    获取输入参数
    :param action_select: 输入参数 调试情况可以传入
    :param input_data: 输入参数 调试情况可以传入
    :param app_name: 应用名称
    :return: 参数字段
    """
    if input_data is None:
        input_data = sys.argv[1]
    input_json = unquote(input_data)
    param = json.loads(input_json)
    if action_select is None:
        action_select = sys.argv[2].strip()
    if action_select is None or action_select == '':
        get_response_json('action is null!', 'Failure')
    if param and str(param.get('appName', '')).upper() == app_name:
        actions = param.get('actions')
        if actions is None or len(actions) == 0:
            return get_response_json('actions is null', 'Failure')
        for action in actions:
            action_name = action.get('name')
            parameters = action.get('parameters')
            if action_name == action_select:
                param_dict = {}
                for param_item in parameters:
                    param_dict[param_item['name']] = get_param_value(param_item)
                return param_dict
        get_response_json('no action match!', 'Failure')
    else:
        return get_response_json('config param error', 'Failure')
