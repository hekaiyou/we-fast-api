import os
import apis.apis_urls as apis_urls
from config import Settings
from typing import Optional
from datetime import datetime
from functools import lru_cache
from pymongo import ASCENDING, DESCENDING
from core.dynamic import get_role_permissions, get_apis_configs
from core.security import get_token_data, TokenData
from fastapi import Depends, HTTPException, Query, status, Request


@lru_cache()
def get_base_settings():
    '''
    全局依赖项: 获取基础环境变量 (仅创建一次)
    依赖项示例: settings: Settings = Depends(get_base_settings)
    依赖项示例: settings = get_base_settings()
    '''
    return Settings(
        _env_file=
        f'{os.path.dirname(os.path.dirname(os.path.realpath(__file__)))}/.env',
        _env_file_encoding='utf-8',
    )


@lru_cache()
def get_api_routes():
    ''' 全局依赖项: 获取 API 路由 (仅创建一次) '''
    routes = {}
    for r in apis_urls.router.routes:
        ritem = r.__dict__
        if '/open/' not in ritem['path'] and '/free/' not in ritem['path']:
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
        description='示例: field1 asc,field2 desc',
        regex='^.+\s+(asc|desc)*$',
    ),
    start_time: Optional[int] = Query(
        default=None,
        ge=1640966400000,
        le=4796640000000,
    ),
    end_time: Optional[int] = Query(
        default=None,
        ge=1640966400000,
        le=4796640000000,
    ),
    time_field: Optional[str] = Query(
        default='create_time',
        regex='^[a-zA-Z]\w{2,31}$',
    ),
):
    ''' 全局依赖项: 获取分页参数 '''
    sort_list = []
    if orderby:
        # 整理请求参数中的筛排序列表
        for order in orderby.split(','):
            order_kv = order.strip().split(' ')
            if len(order_kv) == 2 and (
                    order_kv[1] == 'asc'
                    or order_kv[1] == 'desc') and order_kv[0].strip() != '':
                if order_kv[1] == 'asc':
                    sort_list.append((order_kv[0], ASCENDING))
                elif order_kv[1] == 'desc':
                    sort_list.append((order_kv[0], DESCENDING))
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail='排序参数 orderby 格式错误',
                )
    time_te = {}
    if start_time:
        time_te['$gte'] = datetime.fromtimestamp(
            float(format(start_time / 1000, '.3f')))
    if end_time:
        time_te['$lte'] = datetime.fromtimestamp(
            float(format(end_time / 1000, '.3f')))
    if start_time and end_time:
        if not time_te['$lte'].__gt__(time_te['$gte']):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='结束时间必须大于开始时间',
            )
    return {
        'skip': skip,
        'limit': limit,
        'sort_list': sort_list,
        'time_field': time_field,
        'time_te': time_te
    }


async def verify_api_permission(
    request: Request,
    current_token: TokenData = Depends(get_token_data),
    routes: dict = Depends(get_api_routes)):
    ''' 全局依赖项: 验证 API 访问权限 '''
    if current_token.user_id == 'ExemptIP' and current_token.role_id == 'ExemptIP':
        return
    path_key = f'{request.scope["method"]} {request.scope["path"]}'
    if request.path_params:
        for param_k, param_v in request.path_params.items():
            path_key = path_key.replace(param_v, '{%s}' % (param_k))
    if '/open/' not in path_key:
        if current_token.user_id and '/free/' not in path_key:
            if not routes[path_key]['name'] in get_role_permissions(
                    current_token.role_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f'无 {routes[path_key]["summary"]} 权限',
                )


async def get_view_request(request: Request):
    ''' 全局依赖项: 获取页面访问的请求内容 '''
    return {'request': request, 'settings': get_apis_configs('bases')}


class aiwrap:
    ''' 全局依赖项: 提取解析后再还原 FastAPI 响应 '''

    def __init__(self, obj):
        self._it = iter(obj)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            value = next(self._it)
        except StopIteration:
            raise StopAsyncIteration
        return value
