import os
import time
from loguru import logger
from datetime import date
from apis.bases.models import NoPaginate
from fastapi.responses import FileResponse
from fastapi import APIRouter, HTTPException, status

router = APIRouter(
    prefix='/logs',
)

'''
# 调用参考代码, 先导入模块
from loguru import logger
# 再选择输出什么级别的消息
logger.debug('调试日志')
logger.info('信息日志')
logger.warning('警告日志')
logger.error('异常日志')
'''

# 定位到项目根目录, 再定位到 logs 日志目录
log_path = os.path.join(
    os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.realpath(__file__))
    )),
    'logs',
)
# 创建 logs 日志目录
if not os.path.exists(log_path):
    os.mkdir(log_path)
# 生成当天的日志文件路径
log_path_info = os.path.join(log_path, 'loguru.log')
# 每天凌晨创建新文件, 保留 30 天的日志文件, 开启异步记录
# format='{process} | {thread} | {time:%Y-%m-%d %H:%M:%S.%f} | {level} | {name}:{function}:{line} - {message}',
logger.add(
    log_path_info,
    rotation='00:00',
    retention='30 days',
    enqueue=True,
    level='DEBUG',
    format='{time:%Y-%m-%d %H:%M:%S.%f} - {name}:{function}:{line}\n<{level}>{message}</{level}>',
)


@router.get(
    '/',
    summary='读取日志 (全量)',
)
async def read_logs_all(log_date: date):
    all_item = []
    if time.strftime('%Y-%m-%d', time.localtime(time.time())) == str(log_date):
        all_item.append({'file': 'loguru'})
    exclude_file_path = ['.gitignore', 'loguru.log']
    for file_path in os.listdir(log_path):
        if not file_path in exclude_file_path:
            if str(log_date) in file_path:
                all_item.append({'file': file_path[:-4]})
    return NoPaginate(all_item=all_item, total=len(all_item))


@router.get(
    '/file/',
    summary='读取日志文件',
)
async def read_logs_file(snippet: str):
    path = f'{log_path}/{snippet}.log'
    if os.path.exists(path):
        return FileResponse(
            path=path,
            media_type='text/plain',
            filename=f'{snippet}.log',
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='找不到日志',
        )
