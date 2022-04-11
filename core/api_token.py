import os
import random
import string
import requests
from datetime import timedelta
from core.validate import str_to_oid
from core.storage import save_raw_file, FILES_PATH
from core.model import Token, TokenData
from fastapi.responses import FileResponse
from core.dynamic import get_username_binding
from fastapi.encoders import jsonable_encoder
from core.dependencies import get_settings, Settings
from fastapi.security import OAuth2PasswordRequestForm
from core.database import get_collection, doc_create, doc_update
from apis.users.models import UserGlobal, COL_USER, UserUpdateMe, COL_ROLE
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
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), settings: Settings = Depends(get_settings)):
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
    role = {'title': 'Default', 'permissions': settings.user_default_permission}
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
    for binding_k, binding_v in get_username_binding().items():
        for field in binding_v:
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
async def create_token_avata(file: UploadFile = File(...), current_token: TokenData = Depends(get_token_data)):
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
async def read_token_avata(current_token: TokenData = Depends(get_token_data)):
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


@router.get(
    '/wechat/',
    response_model=Token,
    summary='微信登录以获取访问令牌',
)
async def wechat_login_for_access_token(code: str, settings: Settings = Depends(get_settings)):
    wechat_response = requests.get(
        f'https://api.weixin.qq.com/sns/jscode2session?appid={settings.wechat_app_id}&secret={settings.wechat_app_secret}&js_code={code}&grant_type=authorization_code')
    if wechat_response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='WeChat authorization request failed',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    # wechat_json['session_key'] 微信服务器给开发者服务器颁发的身份凭证
    wechat_json = wechat_response.json()
    if 'errmsg' in wechat_json:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f'WeChat authorized login failed ({wechat_json["errmsg"]})',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    user_col = get_collection(COL_USER)
    # 判断微信端用户是否已存在
    user_filter = {'bind.wechat': wechat_json['openid']}
    user = user_col.find_one(user_filter)
    if not user:
        doc_create(user_col, {
            'username': wechat_json['openid'],
            'email': None,
            'full_name': None,
            'disabled': False,
            'password': get_password_hash(''.join(random.sample(string.ascii_letters + string.digits, 16))),
            'role_id': '',
            'source': 'WeChat',
            'avata': '',
            'bind': {'wechat': wechat_json['openid']},
        })
        user = user_col.find_one(user_filter)
    role = {'title': 'Default', 'permissions': settings.user_default_permission}
    if user['role_id']:
        role = get_collection(COL_ROLE).find_one({
            '_id': str_to_oid(user['role_id']),
        })
    # 生成访问令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'sub': f'{user["_id"]}:{user["role_id"]}'},
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type='Bearer', role_title=role['title'], role_permissions=role['permissions'])
