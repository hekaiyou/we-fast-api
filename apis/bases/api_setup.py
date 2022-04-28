from fastapi import APIRouter
from core.dynamic import set_apis_configs, get_apis_configs

router = APIRouter(
    prefix='/setup',
)


@router.put(
    '/',
    summary='更新设置',
)
async def update_setup():
    return {}
