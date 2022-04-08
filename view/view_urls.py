import os
import importlib
from fastapi import APIRouter

router = APIRouter(
    prefix='/view',
    dependencies=[],
)

exclude_dir_path = ['view_urls.py', '__init__.py', '__pycache__', 'public']
# 自动查找可用的 API 模块并添加路由
for dir_path in os.listdir('view/'):
    if not dir_path in exclude_dir_path:
        if os.path.exists(f'view/{dir_path}/routing.py'):
            module_name = f'view.{dir_path}.routing'
            meta_class = importlib.import_module(module_name)
            router.include_router(meta_class.router)
