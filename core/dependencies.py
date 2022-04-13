import apis.apis_urls as apis_urls
from config import Settings
from typing import Optional
from functools import lru_cache
from pymongo import ASCENDING, DESCENDING
from core.dynamic import get_role_permissions
from core.security import get_token_data, TokenData
from fastapi import Depends, HTTPException, Query, status, Request, Cookie


@lru_cache()
def get_settings():
    '''
    全局依赖项: 获取环境变量 (仅创建一次)
    依赖项示例: settings: Settings = Depends(get_settings)
    依赖项示例: settings = get_settings()
    '''
    return Settings()


@lru_cache()
def get_api_routes():
    ''' 全局依赖项: 获取 API 路由 (仅创建一次) '''
    routes = {}
    for r in apis_urls.router.routes:
        ritem = r.__dict__
        if not '/open/' in ritem['path']:
            routes[f'{list(ritem["methods"])[0]} {ritem["path"]}'] = {
                'name': ritem['name'],
                'tag': ritem['tags'][0],
                'summary': ritem['summary'],
            }
    return routes


async def get_paginate_parameters(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    orderby: Optional[str] = Query(
        default=None,
        description='Example: field1 asc,field2 desc',
        regex='^.+\s+(asc|desc)*$',
    ),
):
    ''' 全局依赖项: 获取分页参数 '''
    sort_list = []
    if orderby:
        # 整理请求参数中的筛排序列表
        for order in orderby.split(','):
            order_kv = order.strip().split(' ')
            if len(order_kv) == 2 and (order_kv[1] == 'asc' or order_kv[1] == 'desc') and order_kv[0].strip() != '':
                if order_kv[1] == 'asc':
                    sort_list.append((order_kv[0], ASCENDING))
                elif order_kv[1] == 'desc':
                    sort_list.append((order_kv[0], DESCENDING))
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail='The sort parameter orderby is malformed',
                )
    return {'skip': skip, 'limit': limit, 'sort_list': sort_list}


async def verify_api_permission(request: Request, current_token: TokenData = Depends(get_token_data), routes: dict = Depends(get_api_routes)):
    ''' 全局依赖项: 验证 API 访问权限 '''
    path_key = f'{request.scope["method"]} {request.scope["path"]}'
    if request.path_params:
        for param_k, param_v in request.path_params.items():
            path_key = path_key.replace(param_v, '{%s}' % (param_k))
    if current_token.role_id:
        if not routes[path_key]['name'] in get_role_permissions(current_token.role_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f'No {routes[path_key]["summary"]} permission',
            )


async def get_view_request(
    request: Request,
    token: Optional[str] = Cookie(None),
    permission: Optional[str] = Cookie(None),
    settings: Settings = Depends(get_settings),
):
    pass
