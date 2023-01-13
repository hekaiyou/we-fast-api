from time import time
from typing import Optional
from .utils import update_bind_username
from core.security import get_password_hash
from fastapi.encoders import jsonable_encoder
from core.storage import remove_file, FILES_PATH
from core.dependencies import get_paginate_parameters
from fastapi import APIRouter, Depends
from apis.bases.api_me import read_me_avata_file
from apis.bases.models import Paginate, TokenData
from .models import COL_USER, UserRead, UserCreate, UserUpdate
from core.database import paginate_find, doc_create, doc_update, doc_read, doc_delete
from .validate import UserObjIdParams, check_user_username, check_role_id, check_user_email

router = APIRouter(prefix='/user', )


@router.post(
    '/',
    response_model=UserRead,
    summary='创建用户',
)
async def create_user(create_data: UserCreate):
    # 保证用户名和邮箱地址的唯一性逻辑
    check_user_username(create_data.username)
    check_user_email(create_data.email)
    if create_data.role_id:
        check_role_id(create_data.role_id)
    create_json = jsonable_encoder(create_data)
    create_json['password'] = get_password_hash(create_data.password)
    create_json['source'] = 'Admin'
    create_json['avata'] = ''
    create_json['bind'] = {'wechat': '', 'email': ''}
    create_json['verify'] = {
        'email': {
            'code': '',
            'create': None,
            'value': ''
        }
    }
    doc_create(COL_USER, create_json)
    return create_json


@router.get(
    '/{user_id}/',
    response_model=UserRead,
    summary='读取用户',
)
async def read_user(user_id: UserObjIdParams):
    return UserRead(**doc_read(COL_USER, {'_id': user_id}))


@router.get(
    '/',
    response_model=Paginate,
    summary='读取用户 (分页)',
)
async def read_user_page(
    paginate: dict = Depends(get_paginate_parameters),
    username: Optional[str] = None,
    full_name: Optional[str] = None,
    email: Optional[str] = None,
    source: Optional[str] = None,
):
    query_content = {}
    if username:
        # 使用正则表达式查询用户名
        query_content['username'] = {'$regex': username}
    if full_name:
        query_content['full_name'] = {'$regex': full_name}
    if email:
        query_content['email'] = {'$regex': email}
    if source:
        query_content['source'] = source
    results = await paginate_find(
        collection=COL_USER,
        paginate_parameters=paginate,
        query_content=query_content,
        item_model=UserRead,
    )
    return results


@router.put(
    '/{user_id}/',
    response_model=UserUpdate,
    summary='更新用户',
)
async def update_user(user_id: UserObjIdParams, update_data: UserUpdate):
    # 集合中存储的用户数据
    doc_before_update = doc_read(COL_USER, {'_id': user_id})
    # 使用 集合中存储的用户数据 创建一个 用户数据模型实例
    model_before_update = UserUpdate(**doc_before_update)
    # 生成一个只包含显式设置参数 (排除隐式设置的默认值参数) 的数据
    update_json = update_data.dict(exclude_unset=True)
    # 为 用户数据模型实例 创建 模型实例副本, 用接收的数据更新其属性
    updated_model = model_before_update.copy(update=update_json)
    # 用户名和邮箱地址的防重复逻辑
    if model_before_update.username != updated_model.username:
        check_user_username(updated_model.username)
    if model_before_update.email != updated_model.email:
        check_user_email(updated_model.email)
    if updated_model.role_id:
        check_role_id(updated_model.role_id)
    # 把 模型实例副本 转换为适配 JSON 的数据, 再保存至数据库集合
    doc_update(COL_USER, {'_id': user_id}, jsonable_encoder(updated_model))
    if doc_before_update['username'] != updated_model.username:
        update_bind_username(
            stored_name=doc_before_update['username'],
            update_name=updated_model.username,
        )
    return updated_model


@router.delete(
    '/{user_id}/',
    summary='删除用户',
)
async def delete_user(user_id: UserObjIdParams):
    doc_before_delete = doc_read(COL_USER, {'_id': user_id})
    doc_delete(COL_USER, {'_id': user_id})
    # 同步处理全部绑定用户名的集合及其字段内容
    update_name = f'[deleted{int(time())}]{doc_before_delete["username"]}'
    if doc_before_delete['username'] != update_name:
        update_bind_username(
            stored_name=doc_before_delete['username'],
            update_name=update_name,
        )
    if doc_before_delete['avata']:
        # 删除头像文件
        await remove_file([FILES_PATH, 'avata', str(user_id)])
    return {}


@router.get(
    '/{user_id}/avata/open/',
    summary='读取用户头像文件 (开放)',
)
async def read_user_avata_file(user_id: UserObjIdParams):
    results = await read_me_avata_file(
        TokenData(user_id=str(user_id), role_id=''))
    return results
