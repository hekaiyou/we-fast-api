import os
import shutil
import hashlib
import requests
from PIL import Image
from datetime import datetime
from tempfile import NamedTemporaryFile
from fastapi import HTTPException, status

FILES_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'files')


async def save_url_file(url: str,
                        directory: list,
                        filename: str = None,
                        type_check: list = []):
    """ 保存URL文件 """
    url_md5 = hashlib.md5(url.encode('utf8')).hexdigest()
    save_path = os.path.join(FILES_PATH, *directory)
    if not os.path.isdir(save_path):
        os.makedirs(save_path)
    if filename:
        file_path = os.path.join(save_path, filename)
    else:
        file_path = os.path.join(save_path, url_md5)
    try:
        res = requests.get(url, stream=True)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'文件资源地址无法连接: {e}',
        )
    if res.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='文件资源地址不可用',
        )
    file_type = res.headers.get('Content-Type', '')
    if type_check:
        if file_type.split('/')[0] not in type_check:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'文件不是 {"|".join(type_check)} 类型',
            )
    with open(file_path, 'wb') as f_obj:
        for chunk in res.iter_content(chunk_size=1024):
            if chunk:
                f_obj.write(chunk)
    url_filename = url_md5
    if file_type:
        url_filename += f'.{file_type.split("/")[1]}'
    return {
        'md5': url_md5,
        'path': os.path.join(*directory),
        'type': file_type,
        'filename': url_filename,
    }


async def save_raw_file(file: NamedTemporaryFile,
                        directory: list,
                        filename: str = None,
                        type_check: list = []):
    """ 保存原始文件 """
    if type_check:
        if file.content_type.split('/')[0] not in type_check:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'文件不是 {"|".join(type_check)} 类型',
            )
    contents = await file.read()  # 读取文件二进制对象
    file_md5 = hashlib.md5(contents).hexdigest()  # 计算文件 MD5
    save_path = os.path.join(FILES_PATH, *directory)
    if not os.path.isdir(save_path):
        os.makedirs(save_path)  # 创建新目录
    if filename:
        # 使用 filename 参数生成完整的保存路径
        file_path = os.path.join(save_path, filename)
    else:
        # 将文件 MD5 作为新的文件名, 生成完整的保存路径
        file_path = os.path.join(save_path, file_md5)
    with open(file_path, 'wb') as f:
        f.write(contents)  # 保存文件
    return {
        'md5': file_md5,
        'path': os.path.join(*directory),
        'type': file.content_type,
        'filename': file.filename,
    }


async def save_file_by_date(file: NamedTemporaryFile, directory: list):
    """ 按日期划分子目录保存文件 """
    save_datetime = datetime.now()
    directory.extend([
        str(save_datetime.year),
        str(save_datetime.month),
        str(save_datetime.day),
    ])
    save_result = await save_raw_file(file, directory)
    return save_result


async def remove_file(path: list):
    """ 删除文件 """
    remove_path = os.path.join(FILES_PATH, *path)
    # 判断文件是否存在, 再删除文件
    if os.path.exists(remove_path):
        os.remove(remove_path)
    other_path = os.path.join(FILES_PATH, *path[:-1])
    if os.path.exists(os.path.join(other_path, f'{path[-1:][0]}_t')):
        os.remove(os.path.join(other_path, f'{path[-1:][0]}_t'))


async def remove_dirs(path: list):
    """ 删除目录 """
    remove_path = os.path.join(FILES_PATH, *path)
    # 判断文件夹是否存在, 再删除文件夹
    if os.path.exists(remove_path):
        shutil.rmtree(remove_path)


async def generate_thumbnail(path: list, size: tuple):
    """ 生成图像文件的缩略图文件 """
    original_path = os.path.join(FILES_PATH, *path)
    thumbnail_path = os.path.join(FILES_PATH, *path[:-1], f'{path[-1:][0]}_t')
    if os.path.exists(thumbnail_path):
        return thumbnail_path
    im = Image.open(original_path)
    im.thumbnail(size)
    im.save(thumbnail_path, im.format)
    return thumbnail_path
