import random
import string
import requests
from datetime import timedelta
from core.validate import str_to_oid
from core.model import Token, TokenData
from core.database import get_collection, doc_create
from apis.users.models import UserGlobal, COL_USER
from core.dependencies import get_settings, Settings
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException, status
from core.security import authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, get_token_data, get_password_hash

router = APIRouter(
    prefix='/token',
    tags=['token'],
)


@router.get(
    '/',
    summary='微信登录以获取访问令牌',
)
async def weixin_login_for_access_token(code: str, settings: Settings = Depends(get_settings)):
    weixin_response = requests.get(
        f'https://api.weixin.qq.com/sns/jscode2session?appid={settings.weixin_app_id}&secret={settings.weixin_app_secret}&js_code={code}&grant_type=authorization_code')
    if weixin_response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='WeChat authorization request failed',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    weixin_json = weixin_response.json()
    if 'errmsg' in weixin_json:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f'WeChat authorized login failed ({weixin_json["errmsg"]})',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    user_col = get_collection(COL_USER)
    # 判断微信端用户是否已存在
    user_filter = {'weixin_open_id': weixin_json['openid']}
    user = user_col.find_one(user_filter)
    if not user:
        doc_create(user_col, {
            'weixin_open_id': weixin_json['openid'],
            'password': get_password_hash(''.join(random.sample(string.ascii_letters + string.digits, 16))),
            'source': 'WeChat',
        })
        user = user_col.find_one(user_filter)
    print(user)
    # weixin_json['session_key'] 微信服务器给开发者服务器颁发的身份凭证
    return weixin_json


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
            detail='Wrong user name or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='User has been disabled',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    # 根据令牌过期权限, 获取令牌过期时间
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # 创建访问令牌, 同时放置唯一且是字符串的 sub 标识
    access_token = create_access_token(
        data={'sub': f'{user.id}:{user.role_id}'},
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type='bearer')


@router.get(
    '/me',
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
