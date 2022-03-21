from typing import Optional
from jose import JWTError, jwt
from core.model import TokenData
from datetime import datetime, timedelta
from passlib.context import CryptContext
from apis.users.models import UserGlobal
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, Depends, status

# 用于哈希和校验密码的 PassLib 上下文
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
# 使用命令生成一个安全的随机密钥: `openssl rand -hex 32`
SECRET_KEY = '2203a6a1be54a1ab3afad0e5ca16de1dfe2ee384f13fe4b710c0b16359db9983'
# 设定 JWT 令牌签名算法
ALGORITHM = 'HS256'
# 设置令牌过期时间 (分钟)
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# 依赖项 `oauth2_scheme` 会返回 `str` 类型的 `token` 令牌, 工作流:
# 1. 检查请求 `header` 中是否加上 `Authorization Bearer token` 值
# 2. 如果 `header` 中找不到, 而且请求参数中没有 `token` 值, 直接响应 401 异常
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/token')


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


async def get_token_data(token: str = Depends(oauth2_scheme)):
    ''' 依赖项: 获取当前令牌数据 '''
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Unable to verify credentials',
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
