from datetime import timedelta
from core.validate import str_to_oid
from core.database import get_collection
from .models import Token, COL_USER, COL_ROLE
from core.dynamic import get_role_permissions
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException, status
from core.security import authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token

router = APIRouter(prefix='/token', )


@router.post(
    '/open/',
    response_model=Token,
    summary='创建接口访问令牌 (开放)',
)
async def create_api_access_token(
        form_data: OAuth2PasswordRequestForm = Depends()):
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
            '_id':
            str_to_oid(user.role_id),
        })
    # 根据令牌过期权限, 获取令牌过期时间
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # 创建访问令牌, 同时放置唯一且是字符串的 sub 标识
    access_token = create_access_token(
        data={'sub': f'{user.id}:{user.role_id}'},
        expires_delta=access_token_expires,
    )
    return Token(
        access_token=access_token,
        token_type='Bearer',
        username=user.username,
        role_title=role['title'],
        role_permissions=role['permissions'],
        expires_minutes=ACCESS_TOKEN_EXPIRE_MINUTES,
        full_name=user.full_name,
        incomplete=(not user.email),
    )
