from core.model import NoPaginate
from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter, HTTPException, status
from core.database import get_collection, doc_create, doc_update
from .validate import RoleObjIdParams, check_role_title, check_role_permissions
from .models import COL_ROLE, RoleRead, RoleUpdate, COL_USER, RoleBase, SyncedWorkerRead
from core.dynamic import set_role_permissions, revise_settings, get_worker_id, get_role_permissions

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
async def read_role(role_id: RoleObjIdParams):
    if str(role_id) == '100000000000000000000001':
        return {
            '_id': '100000000000000000000001',
            'title': 'Default',
            'permissions': get_role_permissions(''),
        }
    return RoleRead(**(get_collection(COL_ROLE).find_one({'_id': role_id})))


@router.post(
    '/',
    response_model=RoleRead,
    summary='创建角色',
)
async def create_role(role_create: RoleBase):
    role_col = get_collection(COL_ROLE)
    check_role_permissions(role_create.permissions)
    check_role_title(role_create.title)
    role_json = jsonable_encoder(role_create)
    doc_create(role_col, role_json)
    set_role_permissions(role_col)  # 刷新全局角色权限变量
    return RoleRead(**role_json)


@router.delete(
    '/{role_id}/',
    summary='删除角色',
)
async def delete_role(role_id: RoleObjIdParams):
    role_col = get_collection(COL_ROLE)
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
    response_model=SyncedWorkerRead,
    summary='更新角色',
)
async def update_role(role_id: RoleObjIdParams, role_update: RoleUpdate):
    role_col = get_collection(COL_ROLE)
    if role_update.permissions:
        check_role_permissions(role_update.permissions)
    if str(role_id) == '100000000000000000000001':
        revise_settings('user_default_permission', role_update.permissions)
        set_role_permissions(role_col)
        return {'wid': get_worker_id([])}
    stored_role_data = role_col.find_one({'_id': role_id})
    stored_role_model = RoleUpdate(**stored_role_data)
    update_role = role_update.dict(exclude_unset=True)
    updated_role = stored_role_model.copy(update=update_role)
    if stored_role_model.title != updated_role.title:
        check_role_title(updated_role.title)
    doc_update(role_col, stored_role_data, jsonable_encoder(updated_role))
    set_role_permissions(role_col)  # 刷新全局角色权限变量
    return {'wid': get_worker_id([])}
