import os
from fastapi import APIRouter, HTTPException, status
from core.model import NoPaginate
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
                if dir_path == 'bases':
                    all_item.append({'name': 'basal'})
                else:
                    all_item.append({'name': dir_path})
    return NoPaginate(all_item=all_item, total=len(all_item))


@router.get(
    '/{module_name}/',
    response_model=NoPaginate,
    summary='读取设置',
)
async def read_setup(module_name: str):
    if module_name == 'basal':
        module_name = 'bases'
    configs = get_apis_configs(module_name)
    if not configs:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='找不到模块',
        )
    all_item = []
    for config in configs:
        all_item.append({
            'key': config[0], 'value': config[1], 'type': str(type(config[1]))[8:-2],
        })
    return NoPaginate(all_item=all_item, total=len(all_item))


@router.put(
    '/{module_name}/',
    summary='更新设置',
)
async def update_setup(module_name: str):
    if module_name == 'basal':
        module_name = 'bases'
    configs = get_apis_configs(module_name)
    if not configs:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='找不到模块',
        )
    return {}
