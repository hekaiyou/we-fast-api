import random
import string
import requests
from datetime import timedelta
from core.storage import save_url_file
from core.validate import str_to_oid
from core.database import get_collection, doc_create, doc_update
from fastapi import APIRouter, HTTPException, status, Depends
from core.dynamic import get_apis_configs, get_role_permissions
from .models import Token, COL_USER, COL_ROLE, FileURL, TokenData
from core.security import get_password_hash, ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, get_token_data

router = APIRouter(prefix='/wechat', )


@router.get(
    '/token/open/',
    response_model=Token,
    summary='读取微信端访问令牌 (开放)',
)
async def read_wechat_access_token(code: str):
    configs = get_apis_configs('bases')
    if not configs.enable_wechat_app:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='未启用微信小程序支持',
        )
    if not configs.wechat_app_id or not configs.wechat_app_secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='未配置微信小程序相关变量',
        )
    wechat_response = requests.get(
        f'https://api.weixin.qq.com/sns/jscode2session?appid={configs.wechat_app_id}&secret={configs.wechat_app_secret}&js_code={code}&grant_type=authorization_code'
    )
    if wechat_response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='微信授权请求失败',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    # wechat_json['session_key'] 微信服务器给开发者服务器颁发的身份凭证
    wechat_json = wechat_response.json()
    if 'errmsg' in wechat_json:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f'微信授权登录失败 ({wechat_json["errmsg"]})',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    user_col = get_collection(COL_USER)
    # 判断微信端用户是否已存在
    user_filter = {'bind.wechat': wechat_json['openid']}
    user = user_col.find_one(user_filter)
    if not user:
        doc_create(
            user_col, {
                'username':
                wechat_json['openid'],
                'email':
                None,
                'full_name':
                None,
                'disabled':
                False,
                'password':
                get_password_hash(''.join(
                    random.sample(string.ascii_letters + string.digits, 16))),
                'role_id':
                '',
                'source':
                'WeChat',
                'avata':
                '',
                'bind': {
                    'wechat': wechat_json['openid'],
                    'email': ''
                },
                'verify': {
                    'email': {
                        'code': '',
                        'create': None,
                        'value': ''
                    }
                },
            })
        user = user_col.find_one(user_filter)
    if user.get('disabled', False):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='账户已被禁用',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    role = {'title': 'Default', 'permissions': get_role_permissions(None)}
    if user['role_id']:
        role = get_collection(COL_ROLE).find_one({
            '_id':
            str_to_oid(user['role_id']),
        })
    # 生成访问令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'sub': f'{user["_id"]}:{user["role_id"]}'},
        expires_delta=access_token_expires,
    )
    return Token(
        access_token=access_token,
        token_type='Bearer',
        username=user['username'],
        role_title=role['title'],
        role_permissions=role['permissions'],
        expires_minutes=ACCESS_TOKEN_EXPIRE_MINUTES,
        full_name=user['full_name'] if user['full_name'] else '',
        incomplete=(user['username'] == user['bind']['wechat']
                    or not user['email']),
    )


@router.post(
    '/avata/free/',
    summary='创建微信头像 (文件|无权限)',
)
async def create_wechat_avata_file(
    file_url: FileURL, current_token: TokenData = Depends(get_token_data)):
    save_result = await save_url_file(file_url.url, ['avata'],
                                      current_token.user_id, ['image'])
    doc_update(get_collection(COL_USER),
               {'_id': str_to_oid(current_token.user_id)},
               {'avata': save_result['filename']})
    return {}