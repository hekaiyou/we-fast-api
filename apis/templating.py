import os
from fastapi.templating import Jinja2Templates

templates_paths = []
exclude_dir_path = [
    'apis_urls.py', '__init__.py', '__pycache__', 'templating.py'
]
work_path_apis = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
for dir_path in os.listdir(f'{work_path_apis}/apis/'):
    if dir_path not in exclude_dir_path:
        if os.path.exists(f'{work_path_apis}/apis/{dir_path}/views/templates'):
            templates_paths.append(
                f'{work_path_apis}/apis/{dir_path}/views/templates')
templates = Jinja2Templates(directory=templates_paths)
