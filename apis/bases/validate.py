from core.validate import ObjIdParams, ObjectId, str_to_oid
from core.database import get_collection
from .models import COL_ROLE, COL_USER
from fastapi import HTTPException, status
from core.dependencies import get_api_routes


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
    if not set(v).issubset(set(get_api_routes())):
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
    user = get_collection(COL_USER).find_one({
        '_id': str_to_oid(v),
    })
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='令牌无法匹配到用户',
        )
    return user
