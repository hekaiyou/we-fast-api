from datetime import datetime
from random import randint, choice
from .models import COL_ROLE, COL_USER
from fastapi import HTTPException, status
from core.dependencies import get_api_routes
from core.database import get_collection, doc_update
from core.validate import ObjIdParams, ObjectId, str_to_oid


class RoleObjIdParams(ObjIdParams):

    @classmethod
    def validate(cls, v):
        ObjIdParams.validate(v)
        role_id = ObjectId(v)
        if not get_collection(COL_ROLE).count_documents({'_id': role_id}):
            if v != '100000000000000000000001':
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail='找不到角色',
                )
        return role_id


def check_role_title(v):
    role_col = get_collection(COL_ROLE)
    if role_col.count_documents({'title': v}):
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


def check_role_id(v):
    if not get_collection(COL_ROLE).count_documents({'_id': str_to_oid(v)}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='角色 ID 不存在',
        )


class UserObjIdParams(ObjIdParams):

    @classmethod
    def validate(cls, v):
        ObjIdParams.validate(v)
        user_id = ObjectId(v)
        if not get_collection(COL_USER).count_documents({'_id': user_id}):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='找不到用户',
            )
        return user_id


def check_user_username(v):
    user_col = get_collection(COL_USER)
    if user_col.count_documents({'username': v}):
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
    if get_collection(COL_USER).count_documents({'email': v}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='电子邮箱地址已存在',
        )


def get_me_user(v):
    if v == 'ExemptIP':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='当前为免鉴权 IP 访问',
        )
    user = get_collection(COL_USER).find_one({
        '_id': str_to_oid(v),
    })
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
        get_collection(COL_USER),
        {'_id': user_id},
        {
            f'verify.{verify_key}.code': code,
            f'verify.{verify_key}.value': value,
            f'verify.{verify_key}.create': datetime.utcnow(),
        },
    )
    return code


def check_verify_code(code, user_id, verify_key):
    if not code or len(code) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='无效的验证码',
        )
    user_col = get_collection(COL_USER)
    user = user_col.find_one({'_id': user_id})
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
    doc_update(user_col, {'_id': user['_id']}, update_dict)
    return True
