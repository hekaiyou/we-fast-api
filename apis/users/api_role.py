from core.model import NoPaginate
from core.validate import ObjIdParams
from core.database import get_collection, doc_create, doc_update
from core.dependencies import get_api_routes
from fastapi.encoders import jsonable_encoder
from core.dynamic import set_role_permissions
from fastapi import APIRouter, HTTPException, status, Depends
from .models import COL_ROLE, RoleRead, RoleUpdate, RoleCreate, COL_USER

router = APIRouter(
    prefix='/role',
)


@router.get(
    '/',
    response_model=NoPaginate,
    summary='读取角色 (全量)',
)
async def read_role_all():
    all_item = []
    for result in get_collection(COL_ROLE).find({}):
        all_item.append(RoleRead(**result))
    return NoPaginate(all_item=all_item, total=len(all_item))


@router.get(
    '/{role_id}/',
    response_model=RoleRead,
    summary='读取角色',
)
async def read_role(role_id: ObjIdParams):
    role_col = get_collection(COL_ROLE)
    if not role_col.count_documents({'_id': role_id}):
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail='找不到角色',
        )
    return RoleRead(**(get_collection(COL_ROLE).find_one({'_id': role_id})))


@router.post(
    '/',
    response_model=RoleRead,
    summary='创建角色',
)
async def create_role(role: RoleCreate, routes: dict = Depends(get_api_routes)):
    role_col = get_collection(COL_ROLE)
    valid_permissions = []
    for path, route in routes.items():
        valid_permissions.append(route['name'])
    if not set(role.permissions).issubset(set(valid_permissions)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='权限列表中存在无效内容',
        )
    if role_col.count_documents({'title': role.title}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='角色名称已经存在',
        )
    role_json = jsonable_encoder(role)
    doc_create(role_col, role_json)
    set_role_permissions(role_col)  # 刷新全局角色权限变量
    return RoleRead(**role_json)


@router.delete(
    '/{role_id}/',
    summary='删除角色',
)
async def delete_role(role_id: ObjIdParams):
    role_col = get_collection(COL_ROLE)
    if not role_col.count_documents({'_id': role_id}):
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail='找不到角色',
        )
    if get_collection(COL_USER).count_documents({'role_id': str(role_id)}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='角色存在用户绑定关系',
        )
    role_col.delete_one({'_id': role_id})
    set_role_permissions(role_col)  # 刷新全局角色权限变量
    return {}


@router.put(
    '/{role_id}/',
    response_model=RoleUpdate,
    summary='更新角色',
)
async def update_role(role_id: ObjIdParams, role: RoleUpdate):
    role_col = get_collection(COL_ROLE)
    stored_role_data = role_col.find_one({'_id': role_id})
    if not stored_role_data:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail='找不到角色',
        )
    stored_role_model = RoleUpdate(**stored_role_data)
    update_role = role.dict(exclude_unset=True)
    updated_role = stored_role_model.copy(update=update_role)
    if stored_role_model.title != updated_role.title:
        if role_col.count_documents({'title': updated_role.title}):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='角色名称已经存在',
            )
    doc_update(role_col, stored_role_data, jsonable_encoder(updated_role))
    set_role_permissions(role_col)  # 刷新全局角色权限变量
    return updated_role
