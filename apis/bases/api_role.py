from fastapi import APIRouter
from apis.bases.models import NoPaginate
from fastapi.encoders import jsonable_encoder
from core.database import get_collection, doc_create, doc_update, doc_read
from .models import COL_ROLE, RoleRead, RoleUpdate, RoleBase, SyncedWorkerRead
from .validate import RoleObjIdParams, check_role_title, check_role_permissions, check_role_and_user
from core.dynamic import set_role_permissions, revise_settings, get_worker_id, get_role_permissions

router = APIRouter(prefix='/role', )


@router.get(
    '/',
    response_model=NoPaginate,
    summary='读取角色 (全量)',
)
async def read_role_all():
    all_item = []
    for result in doc_read(COL_ROLE, {}, many=True):
        all_item.append(RoleRead(**result))
    return NoPaginate(all_item=all_item, total=len(all_item))


@router.get(
    '/{role_id}/',
    response_model=RoleRead,
    summary='读取角色',
)
async def read_role(role_id: RoleObjIdParams):
    if str(role_id) == '100000000000000000000001':
        # role_id = 100000000000000000000001 = 用户未分配角色时的默认权限
        # 获取环境变量中的值并作为 Default 角色数据返回
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
async def create_role(create_data: RoleBase):
    create_col = get_collection(COL_ROLE)
    # 校验权限列表中的权限ID是否有效
    check_role_permissions(create_data.permissions)
    # 校验角色名称是否可用
    check_role_title(create_data.title)
    create_json = jsonable_encoder(create_data)
    doc_create(create_col, create_json)
    set_role_permissions(create_col)  # 刷新全局角色权限变量
    return RoleRead(**create_json)


@router.delete(
    '/{role_id}/',
    summary='删除角色',
)
async def delete_role(role_id: RoleObjIdParams):
    delete_col = get_collection(COL_ROLE)
    # 校验是否还存在用户被分配当前角色
    check_role_and_user(str(role_id))
    delete_col.delete_one({'_id': role_id})
    set_role_permissions(delete_col)  # 刷新全局角色权限变量
    return {}


@router.put(
    '/{role_id}/',
    response_model=SyncedWorkerRead,
    summary='更新角色',
)
async def update_role(role_id: RoleObjIdParams, update_data: RoleUpdate):
    update_col = get_collection(COL_ROLE)
    if update_data.permissions:
        # 校验权限列表中的权限ID
        check_role_permissions(update_data.permissions)
    if str(role_id) == '100000000000000000000001':
        # user_default_permission = 用户未分配角色时的默认权限
        revise_settings('user_default_permission', update_data.permissions)
        set_role_permissions(update_col)  # 刷新全局角色权限变量
        return {'wid': get_worker_id()}  # 多进程时提供ID以识别当前进程
    doc_before_update = update_col.find_one({'_id': role_id})
    model_before_update = RoleUpdate(**doc_before_update)
    update_json = update_data.dict(exclude_unset=True)
    updated_model = model_before_update.copy(update=update_json)
    if model_before_update.title != updated_model.title:
        # 校验角色名称是否可用
        check_role_title(updated_model.title)
    doc_update(update_col, doc_before_update, jsonable_encoder(updated_model))
    set_role_permissions(update_col)  # 刷新全局角色权限变量
    return {'wid': get_worker_id()}  # 多进程时提供ID以识别当前进程
