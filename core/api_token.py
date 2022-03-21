from datetime import timedelta
from core.validate import str_to_oid
from core.model import Token, TokenData
from apis.users.models import UserGlobal
from core.database import get_collection
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException, status
from core.security import authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, get_token_data

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
        get_collection('user'),
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
    user = get_collection('user').find_one({
        '_id': str_to_oid(current_token.user_id),
    })
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token could not match user',
        )
    return UserGlobal(**user)
