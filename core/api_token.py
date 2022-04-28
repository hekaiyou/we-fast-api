import os
from datetime import timedelta
from core.validate import str_to_oid
from core.storage import save_raw_file, FILES_PATH
from core.model import Token, TokenData
from fastapi.responses import FileResponse
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordRequestForm
from core.dynamic import get_username_binding, get_apis_configs, get_role_permissions
from core.database import get_collection, doc_create, doc_update
from apis.bases.models import UserGlobal, COL_USER, UserUpdateMe, COL_ROLE
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from core.security import authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, get_token_data, get_password_hash

router = APIRouter(
    prefix='/token',
    tags=['token'],
)


@router.post(
    '/',
    response_model=Token,
    summary='登录以获取访问令牌',
)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    '''
    按照 **OAuth 2.0** 协议规定: 客户端/用户必须将 `username` 和 `password` 字段作为表单数据发送
    '''
    user = authenticate_user(
        get_collection(COL_USER),
        form_data.username,
        form_data.password,
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='账户名或密码错误',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='账户已被禁用',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    role = {'title': 'Default', 'permissions': get_role_permissions(None)}
    if user.role_id:
        role = get_collection(COL_ROLE).find_one({
            '_id': str_to_oid(user.role_id),
        })
    # 根据令牌过期权限, 获取令牌过期时间
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # 创建访问令牌, 同时放置唯一且是字符串的 sub 标识
    access_token = create_access_token(
        data={'sub': f'{user.id}:{user.role_id}'},
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type='Bearer', role_title=role['title'], role_permissions=role['permissions'])


@router.get(
    '/me/',
    response_model=UserGlobal,
    summary='读取令牌对应的用户',
)
async def read_token_user(current_token: TokenData = Depends(get_token_data)):
    user = get_collection(COL_USER).find_one({
        '_id': str_to_oid(current_token.user_id),
    })
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token could not match user',
        )
    return UserGlobal(**user)


@router.put(
    '/me/',
    response_model=UserUpdateMe,
    summary='更新令牌对应的用户',
)
async def update_token_user(user: UserUpdateMe, current_token: TokenData = Depends(get_token_data)):
    user_col = get_collection(COL_USER)
    stored_user_data = user_col.find_one({
        '_id': str_to_oid(current_token.user_id),
    })
    if stored_user_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token could not match user',
        )
    stored_user_model = UserUpdateMe(**stored_user_data)
    update_data = user.dict(exclude_unset=True)
    updated_user = stored_user_model.copy(update=update_data)
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
    doc_update(user_col, stored_user_data, jsonable_encoder(updated_user))
    if stored_user_data['username'] != updated_user.username:
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


@router.post(
    '/avata/',
    summary='创建令牌对应的头像文件',
)
async def create_token_avata_file(file: UploadFile = File(...), current_token: TokenData = Depends(get_token_data)):
    user_col = get_collection(COL_USER)
    user = user_col.find_one({
        '_id': str_to_oid(current_token.user_id),
    })
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token could not match user',
        )
    save_result = await save_raw_file(file, ['avata'], current_token.user_id)
    doc_update(user_col, user, {'avata': save_result['filename']})
    return {}


@router.get(
    '/avata/',
    summary='读取令牌对应的头像文件',
)
async def read_token_avata_file(current_token: TokenData = Depends(get_token_data)):
    user_col = get_collection(COL_USER)
    user = user_col.find_one({
        '_id': str_to_oid(current_token.user_id),
    })
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token could not match user',
        )
    if user['avata']:
        return FileResponse(path=os.path.join(FILES_PATH, 'avata', current_token.user_id), filename=user['avata'])
    else:
        return FileResponse(path=os.path.join(FILES_PATH, 'avata', 'default'), filename='default.png')
