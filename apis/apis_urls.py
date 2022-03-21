import apis.users.routing as users_routing
from fastapi import APIRouter, Depends
from core.dependencies import verify_api_permission
# 下面导入 API 模块路由
# 例如: import apis.projects.routing as projects_routing

router = APIRouter(
    prefix='/api',
    dependencies=[Depends(verify_api_permission)],
)

router.include_router(users_routing.router)
# 下面添加 API 模块路由
# 例如: router.include_router(projects_routing.router)
