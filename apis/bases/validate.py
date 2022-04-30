from core.validate import ObjIdParams, ObjectId
from core.database import get_collection
from .models import COL_ROLE
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
