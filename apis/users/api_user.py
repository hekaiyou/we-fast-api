from time import time
from typing import Optional
from core.security import get_password_hash
from fastapi.encoders import jsonable_encoder
from core.dynamic import get_username_binding
from core.validate import ObjIdParams, str_to_oid
from core.dependencies import get_paginate_parameters
from fastapi import APIRouter, Depends, HTTPException, status
from .models import COL_USER, COL_ROLE, UserRead, UserCreate, UserUpdate
from core.database import get_collection, paginate_find, Paginate, doc_create, doc_update

router = APIRouter(
    prefix='/user',
)


@router.post(
    '/',
    response_model=UserRead,
    summary='创建用户',
)
async def create_user(user: UserCreate):
    user_col = get_collection(COL_USER)
    # 保证用户名和邮箱地址的唯一性逻辑
    if user_col.count_documents({'username': user.username}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Username already exists',
        )
    if 'deleted' in user.username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Username wants to do something',
        )
    if user_col.count_documents({'email': user.email}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Email address already exists',
        )
    if user.role_id:
        if not get_collection(COL_ROLE).count_documents({'_id': str_to_oid(user.role_id)}):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Role id does not exist',
            )
    user_json = jsonable_encoder(user)
    user_json['password'] = get_password_hash(user.password)
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
async def update_user(user_id: ObjIdParams, user: UserUpdate):
    user_col = get_collection(COL_USER)
    # 集合中存储的用户数据
    stored_user_data = user_col.find_one({'_id': user_id})
    if not stored_user_data:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail='未找到用户',
        )
    # 使用 集合中存储的用户数据 创建一个 用户数据模型实例
    stored_user_model = UserUpdate(**stored_user_data)
    # 生成一个只包含显式设置参数 (排除隐式设置的默认值参数) 的数据
    update_data = user.dict(exclude_unset=True)
    # 为 用户数据模型实例 创建 模型实例副本, 用接收的数据更新其属性
    updated_user = stored_user_model.copy(update=update_data)
    # 用户名和邮箱地址的防重复逻辑
    if stored_user_model.username != updated_user.username:
        if user_col.count_documents({'username': updated_user.username}):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Username already exists',
            )
    if 'deleted' in updated_user.username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Username wants to do something',
        )
    if stored_user_model.email != updated_user.email:
        if user_col.count_documents({'email': updated_user.email}):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Email address already exists',
            )
    if updated_user.role_id:
        if not get_collection(COL_ROLE).count_documents({'_id': str_to_oid(updated_user.role_id)}):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Role id does not exist',
            )
    # 把 模型实例副本 转换为适配 JSON 的数据, 再保存至数据库集合
    doc_update(user_col, stored_user_data, jsonable_encoder(updated_user))
    if stored_user_data['username'] != updated_user.username:
        # 同步更新全部绑定用户名的集合及其字段内容
        for binding_k, binding_v in get_username_binding().items():
            for field in binding_v:
                if ':array' in field:
                    field = field.split(':')[0]
                    change_item = get_collection(binding_k).find({
                        field: {'$elemMatch': {
                            '$in': [stored_user_data['username']]
                        }}
                    }, {field: 1, '_id': 1})
                    for change in change_item:
                        revise = change[field]
                        for i, v in enumerate(revise):
                            if v == stored_user_data['username']:
                                revise[i] = updated_user.username
                                break
                        doc_update(
                            collection=get_collection(binding_k),
                            filter={'_id': change['_id']},
                            update={field: revise},
                        )
                else:
                    doc_update(
                        collection=get_collection(binding_k),
                        filter={field: stored_user_data['username']},
                        update={field: updated_user.username},
                        many=True
                    )
    return updated_user


@router.delete(
    '/{user_id}/',
    summary='删除用户',
)
async def delete_user(user_id: ObjIdParams):
    user_col = get_collection(COL_USER)
    stored_user_data = user_col.find_one({'_id': user_id})
    if not stored_user_data:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail='未找到用户',
        )
    user_col.delete_one(stored_user_data)
    # 同步处理全部绑定用户名的集合及其字段内容
    update_name = f'[deleted{int(time())}]{stored_user_data["username"]}'
    if stored_user_data['username'] != update_name:
        for binding_k, binding_v in get_username_binding().items():
            for field in binding_v:
                if ':array' in field:
                    field = field.split(':')[0]
                    change_item = get_collection(binding_k).find({
                        field: {'$elemMatch': {
                            '$in': [stored_user_data['username']]
                        }}
                    }, {field: 1, '_id': 1})
                    for change in change_item:
                        revise = change[field]
                        for i, v in enumerate(revise):
                            if v == stored_user_data['username']:
                                revise[i] = update_name
                                break
                        doc_update(
                            collection=get_collection(binding_k),
                            filter={'_id': change['_id']},
                            update={field: revise},
                        )
                else:
                    doc_update(
                        collection=get_collection(binding_k),
                        filter={field: stored_user_data['username']},
                        update={field: update_name},
                        many=True
                    )
    return {}
