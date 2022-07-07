import os
from typing import Optional
from config import Settings
from jose import JWTError, jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from apis.bases.models import UserGlobal, TokenData
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, Depends, status, Request
from core.dynamic import get_apis_configs

base_settings = Settings(
    _env_file=
    f'{os.path.dirname(os.path.dirname(os.path.realpath(__file__)))}/.env',
    _env_file_encoding='utf-8',
)
settings = get_apis_configs('bases')
# 用于哈希和校验密码的 PassLib 上下文
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
# 使用命令生成一个安全的随机密钥: `openssl rand -hex 32`
SECRET_KEY = base_settings.token_secret_key
# 设定 JWT 令牌签名算法
ALGORITHM = 'HS256'
# 设置令牌过期时间 (默认720分钟即12小时)
ACCESS_TOKEN_EXPIRE_MINUTES = settings.token_expire_minute

# 依赖项 `oauth2_scheme` 会返回 `str` 类型的 `token` 令牌, 工作流:
# 1. 检查请求 `header` 中是否加上 `Authorization Bearer token` 值
# 2. 如果 `header` 中找不到, 而且请求参数中没有 `token` 值, 直接响应 401 异常
# 3. 设置 `auto_error=False` 可以关闭自动异常响应, 实现自定义异常响应
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/bases/token/open/',
                                     auto_error=False)


def verify_password(plain_password, password):
    ''' 校验接收的密码是否与存储的哈希值匹配 '''
    return pwd_context.verify(plain_password, password)


def get_password_hash(password):
    ''' 哈希来自用户的密码 '''
    return pwd_context.hash(password)


def get_user(user_col, username: str):
    ''' 查询数据库集合中的用户数据 '''
    result = user_col.find_one({'username': username})
    if result:
        return UserGlobal(**result)


def authenticate_user(user_col, username: str, password: str):
    ''' 认证并返回用户 '''
    user = get_user(user_col, username)
    if not user:
        # 通过用户名判断用户是否存在
        return False
    if not verify_password(password, user.password):
        # 通过 PassLib 上下文判断密码是否正确
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    ''' 生成新的访问令牌 '''
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_token_data(request: Request,
                         token: str = Depends(oauth2_scheme)):
    ''' 依赖项: 获取当前令牌数据 '''
    if request.client.host[:request.client.host.
                           rfind('.')] in settings.token_exempt_ip:
        return TokenData(user_id='ExemptIP', role_id='ExemptIP')
    else:
        if not token:
            if not request.cookies.get('token_s', None):
                if '/open/' not in str(request.url):
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail='未认证',
                        headers={'WWW-Authenticate': 'Bearer'},
                    )
                else:
                    return TokenData(user_id='', role_id='')
            token = request.cookies.get('token_s')
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='无法验证凭据',
            headers={'WWW-Authenticate': 'Bearer'},
        )
        try:
            # 验证 JWT 字符串的签名并解码凭证信息
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            # 在复杂情况下可能需要多个标识, 为避免 ID 冲突, 可以在 `sub` 键的值前加上前缀
            sub_valud: str = payload.get('sub')
            if sub_valud is None:
                raise credentials_exception
            # 解析出用户及其角色的 ID 字符串
            sub_list = sub_valud.split(':')
            return TokenData(user_id=sub_list[0], role_id=sub_list[1])
        except JWTError:
            raise credentials_exception
