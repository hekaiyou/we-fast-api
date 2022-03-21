import os
import shutil
import hashlib
from datetime import datetime
from tempfile import NamedTemporaryFile

FILES_PATH = os.path.join(os.getcwd(), 'files')


async def save_raw_file(file: NamedTemporaryFile, directory: list, filename: str = None):
    ''' 保存原始文件 '''
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
    ''' 按日期划分子目录保存文件 '''
    save_datetime = datetime.now()
    directory.extend([
        str(save_datetime.year),
        str(save_datetime.month),
        str(save_datetime.day),
    ])
    save_result = await save_raw_file(file, directory)
    return save_result


async def remove_file(path: list):
    ''' 删除文件 '''
    remove_path = os.path.join(FILES_PATH, *path)
    # 判断文件是否存在, 再删除文件
    if os.path.exists(remove_path):
        os.remove(remove_path)


async def remove_dirs(path: list):
    ''' 删除目录 '''
    remove_path = os.path.join(FILES_PATH, *path)
    # 判断文件夹是否存在, 再删除文件夹
    if os.path.exists(remove_path):
        shutil.rmtree(remove_path)