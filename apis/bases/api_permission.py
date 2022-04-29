from core.model import NoPaginate
from .models import PermissionRead
from fastapi import APIRouter, Depends
from core.dependencies import get_api_routes

router = APIRouter(
    prefix='/permission',
)


@router.get(
    '/',
    response_model=NoPaginate,
    summary='读取权限 (全量)',
)
async def read_permission(routes: dict = Depends(get_api_routes)):
    all_item = []
    for path, route in routes.items():
        all_item.append(PermissionRead(
            name=route['name'],
            path=path,
            tag=route['tag'],
            summary=route['summary'],
        ))
    return NoPaginate(all_item=all_item, total=len(all_item))
