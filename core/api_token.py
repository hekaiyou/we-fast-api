import os
from core.validate import str_to_oid
from core.storage import save_raw_file, FILES_PATH
from core.model import Token, TokenData
from fastapi.responses import FileResponse
from fastapi.encoders import jsonable_encoder
from core.dynamic import get_username_binding
from core.database import get_collection, doc_update
from apis.bases.models import UserGlobal, COL_USER, UserUpdateMe
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from core.security import get_token_data

router = APIRouter(
    prefix='/token',
    tags=['token'],
)

@router.get(
    '/me/',
    response_model=UserGlobal,
    summary='读取令牌对应的用户',
)
async def read_token_user(current_token: TokenData = Depends(get_token_data)):
    user = get_collection(COL_USER).find_one({
        '_id': str_to_oid(current_token.user_id),
    })
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token could not match user',
        )
    return UserGlobal(**user)


@router.put(
    '/me/',
    response_model=UserUpdateMe,
    summary='更新令牌对应的用户',
)
async def update_token_user(user: UserUpdateMe, current_token: TokenData = Depends(get_token_data)):
    user_col = get_collection(COL_USER)
    stored_user_data = user_col.find_one({
        '_id': str_to_oid(current_token.user_id),
    })
    if stored_user_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token could not match user',
        )
    stored_user_model = UserUpdateMe(**stored_user_data)
    update_data = user.dict(exclude_unset=True)
    updated_user = stored_user_model.copy(update=update_data)
    if stored_user_model.username != updated_user.username:
        if user_col.count_documents({'username': updated_user.username}):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Username already exists',
            )
    if 'deleted' in updated_user.username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Username wants to do something',
        )
    if stored_user_model.email != updated_user.email:
        if user_col.count_documents({'email': updated_user.email}):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Email address already exists',
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


@router.post(
    '/avata/',
    summary='创建令牌对应的头像文件',
)
async def create_token_avata_file(file: UploadFile = File(...), current_token: TokenData = Depends(get_token_data)):
    user_col = get_collection(COL_USER)
    user = user_col.find_one({
        '_id': str_to_oid(current_token.user_id),
    })
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token could not match user',
        )
    save_result = await save_raw_file(file, ['avata'], current_token.user_id)
    doc_update(user_col, user, {'avata': save_result['filename']})
    return {}


@router.get(
    '/avata/',
    summary='读取令牌对应的头像文件',
)
async def read_token_avata_file(current_token: TokenData = Depends(get_token_data)):
    user_col = get_collection(COL_USER)
    user = user_col.find_one({
        '_id': str_to_oid(current_token.user_id),
    })
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token could not match user',
        )
    if user['avata']:
        return FileResponse(path=os.path.join(FILES_PATH, 'avata', current_token.user_id), filename=user['avata'])
    else:
        return FileResponse(path=os.path.join(FILES_PATH, 'avata', 'default'), filename='default.png')
