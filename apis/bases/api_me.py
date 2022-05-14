import os
from core.security import get_token_data
from core.emails import send_simple_mail
from .utils import update_bind_username
from .validate import get_me_user, check_user_username, check_user_email
from fastapi.encoders import jsonable_encoder
from core.database import get_collection, doc_update
from core.storage import save_raw_file, FILES_PATH
from fastapi.responses import StreamingResponse
from .models import TokenData, COL_USER, UserGlobal, UserBase
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File

router = APIRouter(
    prefix='/me',
)


@router.get(
    '/free/',
    response_model=UserGlobal,
    summary='读取我的信息 (无权限)',
)
async def read_me_info(current_token: TokenData = Depends(get_token_data)):
    user = get_me_user(current_token.user_id)
    return UserGlobal(**user)


@router.put(
    '/free/',
    response_model=UserBase,
    summary='更新我的信息 (无权限)',
)
async def update_me_info(user_update: UserBase, current_token: TokenData = Depends(get_token_data)):
    user_col = get_collection(COL_USER)
    stored_user_data = get_me_user(current_token.user_id)
    stored_user_model = UserBase(**stored_user_data)
    update_data = user_update.dict(exclude_unset=True)
    updated_user = stored_user_model.copy(update=update_data)
    if stored_user_model.username != updated_user.username:
        check_user_username(updated_user.username)
    if stored_user_model.email != updated_user.email:
        check_user_email(updated_user.email)
    doc_update(user_col, stored_user_data, jsonable_encoder(updated_user))
    if stored_user_data['username'] != updated_user.username:
        update_bind_username(
            stored_name=stored_user_data['username'], update_name=updated_user.username,
        )
    return updated_user


@router.put(
    '/email/free/',
    summary='验证我的电子邮箱 (无权限)',
)
async def verify_me_email(current_token: TokenData = Depends(get_token_data)):
    send_simple_mail(['何小有<hekaiyou@qq.com>'], '测试邮件',
                     ['测试<a href="http://baidu.com"><span>百度</span></a>内容内容内容', '第二行'])
    return {}


@router.post(
    '/avata/free/',
    summary='创建我的头像文件 (无权限)',
)
async def create_me_avata_file(file: UploadFile = File(...), current_token: TokenData = Depends(get_token_data)):
    user_col = get_collection(COL_USER)
    user = get_me_user(current_token.user_id)
    if file.content_type.split('/')[0] != 'image':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='文件不是图像类型',
        )
    save_result = await save_raw_file(file, ['avata'], current_token.user_id)
    doc_update(user_col, user, {'avata': save_result['filename']})
    return {}


@router.get(
    '/avata/free/',
    summary='读取我的头像文件 (无权限)',
)
async def read_me_avata_file(current_token: TokenData = Depends(get_token_data)):
    user = get_me_user(current_token.user_id)
    if user['avata']:
        path = os.path.join(FILES_PATH, 'avata', current_token.user_id)
        filename = user['avata']
    else:
        path = os.path.join(FILES_PATH, 'avata', 'default')
        filename = 'default.png'

    def iter_file():
        with open(path, mode='rb') as file_like:
            yield from file_like
    return StreamingResponse(iter_file(), media_type=f'image/{filename.split(".")[-1]}')
