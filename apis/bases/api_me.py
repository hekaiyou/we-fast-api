from core.validate import str_to_oid
from fastapi import APIRouter, Depends, HTTPException, status
from core.security import get_token_data
from core.dynamic import get_username_binding
from fastapi.encoders import jsonable_encoder
from core.database import get_collection, doc_update
from .models import TokenData, COL_USER, UserGlobal, UserUpdateMe

router = APIRouter(
    prefix='/me',
)


@router.get(
    '/free/',
    response_model=UserGlobal,
    summary='读取我的信息 (无权限)',
)
async def read_me_info(current_token: TokenData = Depends(get_token_data)):
    user = get_collection(COL_USER).find_one({
        '_id': str_to_oid(current_token.user_id),
    })
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='令牌无法匹配到用户',
        )
    return UserGlobal(**user)


@router.put(
    '/free/',
    response_model=UserUpdateMe,
    summary='更新我的信息',
)
async def update_me_info(user: UserUpdateMe, current_token: TokenData = Depends(get_token_data)):
    user_col = get_collection(COL_USER)
    stored_user_data = user_col.find_one({
        '_id': str_to_oid(current_token.user_id),
    })
    if stored_user_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='令牌无法匹配到用户',
        )
    stored_user_model = UserUpdateMe(**stored_user_data)
    update_data = user.dict(exclude_unset=True)
    updated_user = stored_user_model.copy(update=update_data)
    if stored_user_model.username != updated_user.username:
        if user_col.count_documents({'username': updated_user.username}):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='用户名已存在',
            )
    if 'deleted' in updated_user.username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='用户名想搞事情',
        )
    if stored_user_model.email != updated_user.email:
        if user_col.count_documents({'email': updated_user.email}):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='电子邮箱地址已存在',
            )
    doc_update(user_col, stored_user_data, jsonable_encoder(updated_user))
    if stored_user_data['username'] != updated_user.username:
        for binding_k, binding_v in get_username_binding().items():
            for field in binding_v:
                if ':array' in field:
                    field = field.split(':')[0]
                    change_item = get_collection(binding_k).find({
                        field: {'$elemMatch': {
                            '$in': [stored_user_data['username']]
                        }}
                    }, {field: 1, '_id': 1})
                    for change in change_item:
                        revise = change[field]
                        for i, v in enumerate(revise):
                            if v == stored_user_data['username']:
                                revise[i] = updated_user.username
                                break
                        doc_update(
                            collection=get_collection(binding_k),
                            filter={'_id': change['_id']},
                            update={field: revise},
                        )
                else:
                    doc_update(
                        collection=get_collection(binding_k),
                        filter={field: stored_user_data['username']},
                        update={field: updated_user.username},
                        many=True
                    )
    return updated_user
