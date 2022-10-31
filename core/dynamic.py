import os
import importlib
from json import dumps
from config import Settings
from time import time
from datetime import datetime

DYNAMIC_WORKER_ID = str(time())
DYNAMIC_APIS_CONFIGS = {}
DYNAMIC_ROLE_PERMISSIONS = {}
DYNAMIC_USERNAME_BINDING = {}
DYNAMIC_STARTUP_TASK = []
DYNAMIC_REQUEST_RECORD = []


def get_worker_id(wid_list: list = []):
    global DYNAMIC_WORKER_ID
    if DYNAMIC_WORKER_ID not in wid_list:
        return DYNAMIC_WORKER_ID
    return ''


def get_apis_configs(module):
    """ 获取动态全局变量: 接口配置 """
    global DYNAMIC_APIS_CONFIGS
    if module in DYNAMIC_APIS_CONFIGS:
        return DYNAMIC_APIS_CONFIGS[module]
    else:
        work_path = os.path.dirname(os.path.dirname(
            os.path.realpath(__file__)))
        if os.path.exists(f'{work_path}/apis/{module}/config.py'):
            meta_class = importlib.import_module(f'apis.{module}.config')
            if os.path.exists(f'{work_path}/apis/{module}/.env'):
                DYNAMIC_APIS_CONFIGS[module] = meta_class.Settings(
                    _env_file=f'{work_path}/apis/{module}/.env',
                    _env_file_encoding='utf-8',
                )
            else:
                DYNAMIC_APIS_CONFIGS[module] = meta_class.Settings()
            try:
                DYNAMIC_APIS_CONFIGS[
                    f'{module}_describe'] = meta_class.settings_describe
            except AttributeError:
                DYNAMIC_APIS_CONFIGS[f'{module}_describe'] = {}
            return DYNAMIC_APIS_CONFIGS[module]


def set_apis_configs(module, key, vlaue):
    """ 设置动态全局变量: 接口配置 """
    work_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    revise_settings(key, vlaue, env_path=f'{work_path}/apis/{module}/.env')
    global DYNAMIC_APIS_CONFIGS
    meta_class = importlib.import_module(f'apis.{module}.config')
    DYNAMIC_APIS_CONFIGS[module] = meta_class.Settings(
        _env_file=f'{work_path}/apis/{module}/.env',
        _env_file_encoding='utf-8',
    )


def set_role_permissions(role_col):
    """ 设置动态全局变量: 角色权限 """
    role_permissions = {
        '100000000000000000000001': Settings().user_default_permission
    }
    for result in role_col.find({}):
        role_permissions[str(result['_id'])] = result['permissions']
    global DYNAMIC_ROLE_PERMISSIONS
    DYNAMIC_ROLE_PERMISSIONS = role_permissions


def get_role_permissions(role_id):
    """ 获取动态全局变量: 角色权限 """
    try:
        if not role_id:
            return DYNAMIC_ROLE_PERMISSIONS['100000000000000000000001']
        return DYNAMIC_ROLE_PERMISSIONS[role_id]
    except KeyError as e:
        return []


def set_username_binding(col_name: str, field: list):
    """ 设置动态全局变量: 用户名绑定 """
    global DYNAMIC_USERNAME_BINDING
    DYNAMIC_USERNAME_BINDING[col_name] = field


def get_username_binding():
    """ 获取动态全局变量: 用户名绑定 """
    return DYNAMIC_USERNAME_BINDING


def set_startup_task(task_function):
    """ 设置动态全局变量: 启动任务函数 """
    global DYNAMIC_STARTUP_TASK
    DYNAMIC_STARTUP_TASK.append(task_function)


def get_startup_task():
    """ 获取动态全局变量: 启动任务函数 """
    return DYNAMIC_STARTUP_TASK


def revise_settings(key, value, env_path: str = '.env'):
    """ 修改环境变量文件 """
    if not os.path.exists(env_path):
        os.mknod(env_path)
    with open(env_path, 'r', encoding='utf-8') as file_obj:
        contents = file_obj.read()
    if isinstance(value, list):
        value = dumps(value)
    elif isinstance(value, str):
        value = f"'{value}'"
    match = False
    for content in contents.split('\n'):
        content_kv = content.split('=')
        if key.upper() == content_kv[0]:
            contents = contents.replace(content, f'{content_kv[0]}={value}')
            match = True
    if not match:
        if contents:
            contents += f'\n{key.upper()}={value}'
        else:
            contents += f'{key.upper()}={value}'
    with open(env_path, 'w', encoding='utf-8') as file_obj:
        file_obj.write(contents)


def get_request_record():
    """ 获取动态全局变量: 请求记录 """
    global DYNAMIC_REQUEST_RECORD
    if DYNAMIC_REQUEST_RECORD:
        return DYNAMIC_REQUEST_RECORD.pop()
    else:
        return {}


def set_request_record(request, spend_sec, response):
    """ 设置动态全局变量: 请求记录 """
    if response.status_code in [404, 405, 307]:
        return
    global DYNAMIC_REQUEST_RECORD
    path_key = f'{request.scope["method"]} {request.scope["path"]}'
    if '/static/' in request['root_path']:
        path_key = 'GET /static/'
    elif 'GET /docs' in path_key or path_key == 'GET /openapi.json':
        path_key = 'GET /docs/'
    elif 'GET /redoc' in path_key:
        path_key = 'GET /redoc/'
    else:
        if request.path_params:
            for param_k, param_v in request.path_params.items():
                path_key = path_key.replace(param_v, '{%s}' % (param_k))
    byte = 0
    for header in response.raw_headers:
        if header[0] == b'content-length':
            byte = int(header[1])
            break
    now_dt = datetime.now()
    # 'ip': request.client.host,
    DYNAMIC_REQUEST_RECORD.append({
        'path': path_key,
        'spend_sec': spend_sec,
        'byte': byte,
        'date': str(now_dt.date()),
        'hour': now_dt.time().hour,
        'status': response.status_code,
    })
