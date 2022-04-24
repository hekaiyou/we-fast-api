from config import Settings
import core.dependencies as dependencies

DYNAMIC_ROLE_PERMISSIONS = {}
DYNAMIC_USERNAME_BINDING = {}
DYNAMIC_STARTUP_TASK = []


def set_role_permissions(role_col):
    ''' 设置动态全局变量: 角色权限 '''
    role_permissions = {
        '100000000000000000000001': Settings().user_default_permission
    }
    for result in role_col.find({}):
        role_permissions[str(result['_id'])] = result['permissions']
    global DYNAMIC_ROLE_PERMISSIONS
    DYNAMIC_ROLE_PERMISSIONS = role_permissions


def get_role_permissions(role_id):
    ''' 获取动态全局变量: 角色权限 '''
    try:
        if not role_id:
            return DYNAMIC_ROLE_PERMISSIONS['100000000000000000000001']
        return DYNAMIC_ROLE_PERMISSIONS[role_id]
    except KeyError as e:
        return []


def set_username_binding(col_name: str, field: list):
    ''' 设置动态全局变量: 用户名绑定 '''
    global DYNAMIC_USERNAME_BINDING
    DYNAMIC_USERNAME_BINDING[col_name] = field


def get_username_binding():
    ''' 获取动态全局变量: 用户名绑定 '''
    return DYNAMIC_USERNAME_BINDING


def set_startup_task(task_function):
    ''' 设置动态全局变量: 启动任务函数 '''
    global DYNAMIC_STARTUP_TASK
    DYNAMIC_STARTUP_TASK.append(task_function)


def get_startup_task():
    ''' 获取动态全局变量: 启动任务函数 '''
    return DYNAMIC_STARTUP_TASK
