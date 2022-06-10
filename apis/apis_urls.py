import os
import importlib
from fastapi import APIRouter, Depends
from core.dependencies import verify_api_permission

router = APIRouter(
    prefix='/api',
    dependencies=[Depends(verify_api_permission)],
)

exclude_dir_path = ['apis_urls.py', '__init__.py', '__pycache__']
# 自动查找可用的 API 模块并添加路由
work_path_apis = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
for dir_path in os.listdir(f'{work_path_apis}/apis/'):
    if dir_path not in exclude_dir_path:
        if os.path.exists(f'{work_path_apis}/apis/{dir_path}/routing.py'):
            module_name = f'apis.{dir_path}.routing'
            meta_class = importlib.import_module(module_name)
            router.include_router(meta_class.router)
