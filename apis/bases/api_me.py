import os
from loguru import logger
from datetime import datetime
from random import randint, choice
from core.security import get_token_data
from core.emails import send_simple_mail
from .utils import update_bind_username
from core.dynamic import get_apis_configs
from fastapi.encoders import jsonable_encoder
from core.storage import save_raw_file, FILES_PATH
from core.database import get_collection, doc_update
from .models import TokenData, COL_USER, UserGlobal, UserBase
from fastapi.responses import StreamingResponse, RedirectResponse
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from .validate import get_me_user, check_user_username, check_user_email, check_verify_code

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
    '/email/verify/free/',
    summary='更新我的电子邮箱验证 (无权限)',
)
async def verify_me_email_verify(current_token: TokenData = Depends(get_token_data)):
    user = get_me_user(current_token.user_id)
    if user['verify']['email']['code']:
        if (datetime.utcnow() - user['verify']['email']['create']).seconds < 3600:
            return {'detail': '成功发送验证邮件'}
    if not user.get('email', None):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='找不到电子邮箱信息',
        )
    if user['bind'].get('email', None):
        if user['bind']['email'] == user['email']:
            return {'detail': '电子邮箱已通过验证'}
    code = ''
    for i in range(6):
        n = randint(0, 9)
        b = chr(randint(65, 90))
        s = chr(randint(97, 122))
        code += str(choice([n, b, s]))
    doc_update(
        get_collection(COL_USER), {'_id': user['_id']},
        {'verify.email.code': code,
            'verify.email.value': user['email'], 'verify.email.create': datetime.utcnow(), },
    )
    configs = get_apis_configs('bases')
    send_simple_mail(
        [f'{user["username"]}<{user["email"]}>'],
        '验证电子邮箱',
        [
            f'尊敬的 <b>{user["username"]}({user["full_name"]})</b> :',
            f'请点击 <a href="{configs.app_host}api/bases/me/email/verify/open/?code={code}&username={user["username"]}"><span>验证链接</span></a> 以完成操作!',
            '<i>请保管好您的邮箱, 避免账号被他人盗用</i>',
        ])
    logger.info(f'向 {user["username"]}<{user["email"]}> 发送验证电子邮箱的 {code} 验证码')
    return {'detail': '成功发送验证邮件'}


@router.get(
    '/email/verify/open/',
    summary='读取我的电子邮箱验证 (开放)',
)
async def read_me_email_verify(code: str, username: str):
    check_verify_code(code, username, 'email')
    return RedirectResponse('/view/bases/token/')


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
