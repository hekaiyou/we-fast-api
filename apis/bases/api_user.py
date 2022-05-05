from time import time
from typing import Optional
from .utils import update_bind_username
from core.security import get_password_hash
from fastapi.encoders import jsonable_encoder
from core.storage import remove_file, FILES_PATH
from core.dependencies import get_paginate_parameters
from fastapi import APIRouter, Depends
from .models import COL_USER, UserRead, UserCreate, UserUpdate
from core.database import get_collection, paginate_find, Paginate, doc_create, doc_update
from .validate import UserObjIdParams, check_user_username, check_role_id, check_user_email

router = APIRouter(
    prefix='/user',
)


@router.post(
    '/',
    response_model=UserRead,
    summary='创建用户',
)
async def create_user(user_create: UserCreate):
    user_col = get_collection(COL_USER)
    # 保证用户名和邮箱地址的唯一性逻辑
    check_user_username(user_create.username)
    check_user_email(user_create.email)
    if user_create.role_id:
        check_role_id(user_create.role_id)
    user_json = jsonable_encoder(user_create)
    user_json['password'] = get_password_hash(user_create.password)
    user_json['source'] = 'Admin'
    user_json['avata'] = ''
    user_json['bind'] = {'wechat': ''}
    doc_create(user_col, user_json)
    return user_json


@router.get(
    '/',
    response_model=Paginate,
    summary='读取用户 (分页)',
)
async def read_user_page(
    paginate: dict = Depends(get_paginate_parameters),
    username: Optional[str] = None,
    email: Optional[str] = None,
):
    query_content = {}
    if username:
        # 使用正则表达式查询用户名
        query_content['username'] = {'$regex': username}
    if email:
        query_content['email'] = {'$regex': email}
    results = await paginate_find(
        collection=get_collection(COL_USER),
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
async def update_user(user_id: UserObjIdParams, user_update: UserUpdate):
    user_col = get_collection(COL_USER)
    # 集合中存储的用户数据
    stored_user_data = user_col.find_one({'_id': user_id})
    # 使用 集合中存储的用户数据 创建一个 用户数据模型实例
    stored_user_model = UserUpdate(**stored_user_data)
    # 生成一个只包含显式设置参数 (排除隐式设置的默认值参数) 的数据
    update_data = user_update.dict(exclude_unset=True)
    # 为 用户数据模型实例 创建 模型实例副本, 用接收的数据更新其属性
    updated_user = stored_user_model.copy(update=update_data)
    # 用户名和邮箱地址的防重复逻辑
    if stored_user_model.username != updated_user.username:
        check_user_username(updated_user.username)
    if stored_user_model.email != updated_user.email:
        check_user_email(updated_user.email)
    if updated_user.role_id:
        check_role_id(updated_user.role_id)
    # 把 模型实例副本 转换为适配 JSON 的数据, 再保存至数据库集合
    doc_update(user_col, stored_user_data, jsonable_encoder(updated_user))
    if stored_user_data['username'] != updated_user.username:
        update_bind_username(
            stored_name=stored_user_data['username'], update_name=updated_user.username,
        )
    return updated_user


@router.delete(
    '/{user_id}/',
    summary='删除用户',
)
async def delete_user(user_id: UserObjIdParams):
    user_col = get_collection(COL_USER)
    stored_user_data = user_col.find_one({'_id': user_id})
    user_col.delete_one(stored_user_data)
    # 同步处理全部绑定用户名的集合及其字段内容
    update_name = f'[deleted{int(time())}]{stored_user_data["username"]}'
    if stored_user_data['username'] != update_name:
        update_bind_username(
            stored_name=stored_user_data['username'], update_name=update_name,
        )
    if stored_user_data['avata']:
        # 删除头像文件
        await remove_file([FILES_PATH, 'avata', str(user_id)])
    return {}
