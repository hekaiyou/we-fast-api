import os
import time
from loguru import logger

'''
调用参考信息
logger.debug(f'调试日志')
logger.info(f'信息日志')
logger.success(f'成功日志')
logger.warning(f'警告日志')
logger.error(f'异常日志')
'''

# 定位到项目根目录
basedir = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
# 定位到 logs 日志目录
log_path = os.path.join(basedir, 'logs')
# 创建 logs 日志目录
if not os.path.exists(log_path):
    os.mkdir(log_path)
# 生成当天的日志文件路径
log_path_info = os.path.join(
    log_path,
    f'{time.strftime("%Y-%m-%d")}_info.log'
)
# 每天凌晨创建新文件, 保留 30 天的日志文件, 开启异步记录
logger.add(
    log_path_info,
    rotation='00:01',
    retention='30 days',
    enqueue=True,
    level='INFO',
)
