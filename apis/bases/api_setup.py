import os
from core.dynamic import get_worker_id
from core.model import NoPaginate
from .models import SetupUpdate, SyncedWorkerRead
from fastapi import APIRouter, HTTPException, status
from core.dynamic import set_apis_configs, get_apis_configs

router = APIRouter(
    prefix='/setup',
)


@router.get(
    '/module/',
    response_model=NoPaginate,
    summary='读取设置模块 (全量)',
)
async def read_setup_module_all():
    all_item = []
    exclude_dir_path = ['apis_urls.py', '__init__.py', '__pycache__']
    for dir_path in os.listdir('apis/'):
        if not dir_path in exclude_dir_path:
            if os.path.exists(f'apis/{dir_path}/config.py'):
                all_item.append({'name': f'particle-{dir_path}'})
    return NoPaginate(all_item=all_item, total=len(all_item))


@router.get(
    '/{module_name}/',
    response_model=NoPaginate,
    summary='读取设置',
)
async def read_setup(module_name: str):
    configs = get_apis_configs(module_name[9:])
    if not configs:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='找不到模块',
        )
    all_item = []
    configs_describe = get_apis_configs(f'{module_name[9:]}_describe')
    for config in configs:
        all_item.append({
            'key': config[0], 'value': config[1], 'type': str(type(config[1]))[8:-2], 'describe': configs_describe.get(config[0], ''),
        })
    return NoPaginate(all_item=all_item, total=len(all_item))


@router.put(
    '/{module_name}/',
    response_model=SyncedWorkerRead,
    summary='更新设置',
)
async def update_setup(module_name: str, setup_update: SetupUpdate):
    configs = get_apis_configs(module_name[9:])
    if not configs:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='找不到模块',
        )
    for key, value in setup_update.setups.items():
        set_apis_configs(module=module_name[9:], key=key, vlaue=value)
    return {'wid': get_worker_id(setup_update.synced_wids)}
