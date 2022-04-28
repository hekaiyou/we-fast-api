import os
from core.validate import str_to_oid
from core.storage import save_raw_file, FILES_PATH
from core.model import TokenData
from fastapi.responses import FileResponse
from core.database import get_collection, doc_update
from apis.bases.models import COL_USER
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from core.security import get_token_data

router = APIRouter(
    prefix='/token',
    tags=['token'],
)

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
