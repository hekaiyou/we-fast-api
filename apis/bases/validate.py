from datetime import datetime
from random import randint, choice
from .models import COL_ROLE, COL_USER
from fastapi import HTTPException, status
from core.dependencies import get_api_routes
from core.database import doc_count, doc_read, doc_update
from core.validate import ObjIdParams, str_to_oid


class RoleObjIdParams(ObjIdParams):

    @classmethod
    def validate_doc(cls, oid):
        if not doc_count(COL_ROLE, {'_id': oid}):
            if str(oid) != '100000000000000000000001':
                return False
        return True


class UserObjIdParams(ObjIdParams):

    @classmethod
    def validate_doc(cls, oid):
        return doc_count(COL_USER, {'_id': oid})


def check_role_title(v):
    if doc_count(COL_ROLE, {'title': v}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='角色名称已经存在',
        )
    if 'Default' == v:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='角色 Default 为保留角色',
        )


def check_role_permissions(v):
    routes = get_api_routes()
    valid_permissions = []
    for path, route in routes.items():
        valid_permissions.append(route['name'])
    if not set(v).issubset(set(valid_permissions)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='权限列表中存在无效权限ID',
        )


def check_role_and_user(v):
    if doc_count(COL_USER, {'role_id': v}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='角色存在用户绑定关系',
        )


def check_role_id(v):
    if not doc_count(COL_ROLE, {'_id': str_to_oid(v)}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='角色 ID 不存在',
        )


def check_user_username(v):
    if doc_count(COL_USER, {'username': v}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='用户名已存在',
        )
    if 'deleted' in v:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='用户名中的 deleted 为保留字符串',
        )


def check_user_email(v):
    if doc_count(COL_USER, {'email': v}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='电子邮箱地址已存在',
        )


def check_user_verify_code(user, verify_key):
    if user['verify'][verify_key]['code']:
        if (datetime.utcnow() -
                user['verify'][verify_key]['create']).seconds < 3600:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='验证邮件已经发送',
            )
    if not user.get('email', None):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='找不到电子邮箱信息',
        )


def check_verify_code(code, user_id, verify_key):
    if not code or len(code) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='无效的验证码',
        )
    user = doc_read(COL_USER, {'_id': user_id})
    if not user['verify'][verify_key]['code']:
        return False
    if (datetime.utcnow() -
            user['verify'][verify_key]['create']).seconds > 3600:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='过期的验证码',
        )
    if user['verify'][verify_key]['code'] != code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='错误的验证码',
        )
    update_dict = {
        f'verify.{verify_key}.code': '',
        f'verify.{verify_key}.create': None,
        f'verify.{verify_key}.value': '',
    }
    if verify_key == 'email':
        update_dict[f'bind.{verify_key}'] = user['verify'][verify_key]['value']
    doc_update(COL_USER, {'_id': user['_id']}, update_dict)
    return True


def get_user_username_and_email(user_username):
    user = doc_read(COL_USER, {'username': user_username})
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='用户名不存在',
        )
    return user


def get_me_user(v):
    if v == 'ExemptIP':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='当前为免鉴权 IP 访问',
        )

    user = doc_read(COL_USER, {'_id': str_to_oid(v)})
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='令牌无法匹配到用户',
        )
    return user


def get_verify_code(value, user_id, verify_key):
    code = ''
    for i in range(6):
        n = randint(0, 9)
        b = chr(randint(65, 90))
        s = chr(randint(97, 122))
        code += str(choice([n, b, s]))
    doc_update(
        COL_USER,
        {'_id': user_id},
        {
            f'verify.{verify_key}.code': code,
            f'verify.{verify_key}.value': value,
            f'verify.{verify_key}.create': datetime.utcnow(),
        },
    )
    return code
