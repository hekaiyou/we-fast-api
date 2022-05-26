import os
import importlib
from fastapi import APIRouter

router = APIRouter(
    prefix='/view',
    dependencies=[],
)

exclude_file_path = ['__init__.py', '__pycache__']
# 自动查找可用的 API 模块并添加路由
work_path_view = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
for file_path in os.listdir(f'{work_path_view}/view/routing/'):
    if not file_path in exclude_file_path:
        if os.path.exists(f'{work_path_view}/view/routing/{file_path}'):
            module_name = f'view.routing.{file_path.split(".")[0]}'
            meta_class = importlib.import_module(module_name)
            router.include_router(meta_class.router)
