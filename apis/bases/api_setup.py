import os
from core.dynamic import get_worker_id
from apis.bases.models import NoPaginate
from .models import SetupUpdate, SyncedWorkerRead
from fastapi import APIRouter, HTTPException, status
from core.dynamic import set_apis_configs, get_apis_configs

router = APIRouter(prefix='/setup', )


@router.get(
    '/module/',
    response_model=NoPaginate,
    summary='读取设置模块 (全量)',
)
async def read_setup_module_all():
    all_item = []
    # 在 apis 目录下, 排除非模块目录的其他文件或目录
    exclude_dir_path = [
        'apis_urls.py', '__init__.py', '__pycache__', 'templating.py'
    ]
    work_path = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    for dir_path in os.listdir(f'{work_path}/apis/'):
        if dir_path not in exclude_dir_path:
            # 找到模块目录并取出模块名称
            if os.path.exists(f'{work_path}/apis/{dir_path}/config.py'):
                all_item.append({'name': f'particle-{dir_path}'})
    return NoPaginate(all_item=all_item, total=len(all_item))


@router.get(
    '/{module_name}/',
    response_model=NoPaginate,
    summary='读取设置',
)
async def read_setup(module_name: str):
    # 通过模块名称 (去掉前面的 particle- 字符串) 获取环境变量
    configs = get_apis_configs(module_name[9:])
    if not configs:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='找不到模块',
        )
    all_item = []
    # 通过模块名称获取环境变量的详细信息
    configs_describe = get_apis_configs(f'{module_name[9:]}_describe')
    for config in configs:
        all_item.append({
            'key': config[0],
            'value': config[1],
            'type': str(type(config[1]))[8:-2],
            'describe': configs_describe.get(config[0], ''),
        })
    return NoPaginate(all_item=all_item, total=len(all_item))


@router.put(
    '/{module_name}/',
    response_model=SyncedWorkerRead,
    summary='更新设置',
)
async def update_setup(module_name: str, setup_update: SetupUpdate):
    # 通过模块名称 (去掉前面的 particle- 字符串) 获取环境变量
    configs = get_apis_configs(module_name[9:])
    if not configs:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='找不到模块',
        )
    for key, value in setup_update.setups.items():
        # 逐个更新当前模块的环境变量
        set_apis_configs(module=module_name[9:], key=key, vlaue=value)
    return {'wid': get_worker_id(setup_update.synced_wids)}
