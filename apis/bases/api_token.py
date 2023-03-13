from datetime import timedelta
from core.validate import str_to_oid
from ldap3 import Server, Connection, ALL
from core.database import get_collection, doc_read, doc_create
from .models import Token, COL_USER, COL_ROLE
from .validate import check_user_username, check_user_email
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException, status
from core.dynamic import get_role_permissions, get_apis_configs
from core.security import authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, get_password_hash
from ldap3.core.exceptions import LDAPInvalidCredentialsResult, LDAPSocketOpenError, LDAPInvalidDNSyntaxResult, LDAPAttributeError

router = APIRouter(prefix='/token', )


@router.post(
    '/standard/open/',
    response_model=Token,
    summary='创建标准接口访问令牌 (开放)',
)
async def create_standard_api_access_token(
        form_data: OAuth2PasswordRequestForm = Depends()):
    """
    按照 **OAuth 2.0** 协议规定: 客户端/用户必须将 `username` 和 `password` 字段作为表单数据发送
    """
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
        role = doc_read(COL_ROLE, {'_id': str_to_oid(user.role_id)})
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


@router.post(
    '/ldap/open/',
    response_model=Token,
    summary='创建LDAP接口访问令牌 (开放)',
)
async def create_ldap_api_access_token(
        form_data: OAuth2PasswordRequestForm = Depends()):
    configs = get_apis_configs('bases')
    server = Server(configs.ldap_ad_host, get_info=ALL)
    try:
        main_body = '绑定用户'
        errors = ''
        conn = Connection(
            server,
            user=configs.ldap_ad_bind_dn,
            password=configs.ldap_ad_password,
            auto_bind=True,
            raise_exceptions=True,
        )
        user_filter = configs.ldap_ad_search_filter.split('{}')
        if len(user_filter) != 2:
            raise Exception('用户过滤器缺少 {} 字符')
        result = conn.search(
            search_base=configs.ldap_ad_search_base,
            search_filter=
            f'{user_filter[0]}{form_data.username}{user_filter[1]}',
        )
        main_body = f'用户 {form_data.username} '
        if not result:
            errors = f'{main_body}不存在'
        else:
            Connection(
                server,
                user=conn.response[0]['dn'],
                password=form_data.password,
                auto_bind=True,
                raise_exceptions=True,
            )
            # 通过 conn.response 可以查看详细数据
    except LDAPInvalidCredentialsResult as e:
        if '52e' in e.message:
            errors = f'{main_body}密码不正确'
        elif '775' in e.message:
            errors = f'{main_body}已锁定, 请联系管理员或等待自动解锁'
        elif '533' in e.message:
            errors = f'{main_body}已禁用'
        else:
            errors = f'{main_body}认证失败, 请联系管理员检查该账号'
    except LDAPSocketOpenError:
        errors = '无效的 LDAP/AD 服务器地址'
    except LDAPInvalidDNSyntaxResult:
        errors = f'{main_body}无效的 DN 语法'
    except LDAPAttributeError as e:
        errors = f'属性错误, {e}'
    except Exception as e:
        errors = f'配置错误, {e}'
    finally:
        if errors:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=errors,
                headers={'WWW-Authenticate': 'Bearer'},
            )
    # 判断 LDAP/AD 用户是否已存在
    user_ldap_filter = {'bind.ldap': form_data.username}
    user_ldap = doc_read(COL_USER, user_ldap_filter)
    if not user_ldap:
        # 保证 LDAP/AD 用户名和企业邮箱地址的唯一性
        check_user_username(form_data.username)
        check_user_email(f'{form_data.username}{configs.ldap_ad_email_suffix}')
        doc_create(
            COL_USER, {
                'username': form_data.username,
                'email': f'{form_data.username}{configs.ldap_ad_email_suffix}',
                'full_name': '',
                'disabled': False,
                'password': get_password_hash(form_data.password),
                'role_id': '',
                'source': 'LDAP',
                'avata': '',
                'bind': {
                    'wechat': '',
                    'email': '',
                    'ldap': form_data.username,
                },
                'verify': {
                    'email': {
                        'code': '',
                        'create': None,
                        'value': ''
                    },
                    'password': {
                        'code': '',
                        'create': None,
                        'value': ''
                    }
                },
            })
        user_ldap = doc_read(COL_USER, user_ldap_filter)
    if user_ldap.get('disabled', False):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='账户已被禁用',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    role = {'title': 'Default', 'permissions': get_role_permissions(None)}
    if user_ldap['role_id']:
        role = doc_read(COL_ROLE, {
            '_id': str_to_oid(user_ldap['role_id']),
        })
    # 生成访问令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'sub': f'{user_ldap["_id"]}:{user_ldap["role_id"]}'},
        expires_delta=access_token_expires,
    )
    return Token(
        access_token=access_token,
        token_type='Bearer',
        username=user_ldap['username'],
        role_title=role['title'],
        role_permissions=role['permissions'],
        expires_minutes=ACCESS_TOKEN_EXPIRE_MINUTES,
        full_name=user_ldap['full_name'] if user_ldap['full_name'] else '',
        incomplete=(not user_ldap['email']),
    )
