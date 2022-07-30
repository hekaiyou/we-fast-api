from pydantic import BaseModel
from loguru import logger
from pymongo import MongoClient
from functools import lru_cache
from apis.bases.models import Paginate
from datetime import datetime, timedelta
from pymongo.collection import Collection
from core.dependencies import get_base_settings
from core.security import get_password_hash
from core.dynamic import set_role_permissions, set_startup_task

# MongoDB 数据库客户端
DBClient = None


@lru_cache()
def get_collection(collection_name: str):
    """ 获取 DB 集合 (同一参数仅创建一次) """
    settings = get_base_settings()
    db = DBClient[settings.mongo_db_name]
    # 获取 pymongo.collection.Collection 实例
    collection = db[collection_name]
    return collection


def whether_to_initialize(apis_urls):
    """ 判断数据库连接有效性 (首次连接时初始化) """
    user_col = get_collection('user')
    role_col = get_collection('role')
    try:
        if not user_col.count_documents({}):
            role_result = role_col.find_one({'title': 'SuperAdministrator'})
            if not role_result:
                role_result = role_col.insert_one({
                    'title':
                    'SuperAdministrator',
                    'permissions': [
                        'read_permission_all', 'read_role_all', 'read_role',
                        'create_role', 'delete_role', 'update_role',
                        'create_user', 'read_user_page', 'delete_user',
                        'update_user', 'read_setup_module_all', 'read_setup',
                        'update_setup', 'read_logs_all', 'read_logs_file',
                        'create_logs', 'summary_day_statistics',
                        'summary_hour_statistics', 'read_statistics_all'
                    ],
                    'create_time':
                    datetime.utcnow(),
                    'update_time':
                    datetime.utcnow(),
                })
                role_id = str(role_result.inserted_id)
            else:
                role_id = str(role_result['_id'])
            user_col.insert_one({
                'username': 'admin',
                'email': 'admin@admin.com',
                'full_name': 'Administrator',
                'disabled': False,
                'password': get_password_hash('i23D456'),
                'role_id': role_id,
                'source': 'Initialization',
                'avata': '',
                'bind': {
                    'wechat': '',
                    'email': ''
                },
                'verify': {
                    'email': {
                        'code': '',
                        'create': None,
                        'value': ''
                    }
                },
                'create_time': datetime.utcnow(),
                'update_time': datetime.utcnow(),
            })
            logger.info('第一次连接, 初始化管理员账号: admin / i23D456')
            logger.warning('请尽快登录管理员账号并及时修改密码')
        set_role_permissions(role_col)
    except Exception as e:
        logger.error(f'初始化 MongoDB 连接异常, {e}')


def create_db_client(apis_urls):
    """ 创建 MongoDB 数据库客户端 """
    settings = get_base_settings()
    if settings.mongo_db_username and settings.mongo_db_password:
        # 环境变量中没有认证信息, 走认证连接
        db_client = MongoClient(
            host=settings.mongo_db_host,
            port=settings.mongo_db_port,
            username=settings.mongo_db_username,
            password=settings.mongo_db_password,
        )
    else:
        # 环境变量中没有认证信息, 走直接连接
        db_client = MongoClient(
            host=settings.mongo_db_host,
            port=settings.mongo_db_port,
        )
    global DBClient
    DBClient = db_client
    whether_to_initialize(apis_urls)


def close_db_client():
    """ 关闭 MongoDB 数据库客户端 """
    global DBClient
    DBClient.close()


@lru_cache()
def utc_offset():
    """ UTC 时间与本地时间的差 """
    local_time = datetime.fromtimestamp(0)
    utc_time = datetime.utcfromtimestamp(0)
    return local_time - utc_time


async def paginate_find(collection: Collection,
                        paginate_parameters: dict,
                        query_content: dict,
                        item_model: BaseModel,
                        no_pagin: bool = False):
    """ 分页查询 DB 集合中的数据 """
    if paginate_parameters['time_te']:
        time_te = paginate_parameters['time_te']
        for te_k, te_v in time_te.items():
            time_te[te_k] = te_v - utc_offset()
        query_content[paginate_parameters['time_field']] = time_te
    find_count = collection.count_documents(query_content)
    if not find_count:
        return Paginate(items=[], total=0)
    if no_pagin:
        if paginate_parameters['sort_list']:
            find_results = collection.find(query_content).sort(
                key_or_list=paginate_parameters['sort_list'], )
        else:
            find_results = collection.find(query_content)
    else:
        if paginate_parameters['sort_list']:
            # 包括排序参数的查询
            find_results = collection.find(query_content).sort(
                key_or_list=paginate_parameters['sort_list'], ).skip(
                    skip=paginate_parameters['skip'], ).limit(
                        limit=paginate_parameters['limit'], )
        else:
            # 没有排序参数的查询
            find_results = collection.find(query_content).skip(
                skip=paginate_parameters['skip'], ).limit(
                    limit=paginate_parameters['limit'], )
    items = []
    for result in find_results:
        # 将 UTC 时间转为本地时间
        result['create_time'] += utc_offset()
        result['update_time'] += utc_offset()
        # 使用指定的模型读取查询结果
        if item_model:
            items.append(item_model(**result))
        else:
            items.append(result)
    return Paginate(items=items, total=find_count)


async def paginate_get_cache(paginate_parameters: dict,
                             cache_name: str,
                             cache_key: str,
                             cache_interval_minutes: int = 7):
    """ 分页查询缓存中的数据 """
    cache_key = f'{paginate_parameters["sort_list"]}{paginate_parameters["time_field"]}{paginate_parameters["time_te"]}{cache_key}'
    cache_find = get_collection('paginate_cache').find_one({
        'name': cache_name,
        'key': cache_key,
    })
    if cache_find:
        cache_find['update_time'] += utc_offset()
        if datetime.now() - cache_find['update_time'] > timedelta(
                minutes=cache_interval_minutes):
            # 超过指定间隔分钟数则删除缓存
            get_collection('paginate_cache').delete_many({
                'name': cache_name,
                'key': cache_key,
            })
        else:
            return Paginate(
                items=cache_find['value']
                [paginate_parameters['skip']:paginate_parameters['limit']],
                total=len(cache_find['value']),
            )


async def paginate_set_cache(paginate_parameters: dict, cache_name: str,
                             cache_key: str, cache_value: list):
    """ 分页设置缓存中的数据 """
    cache_key = f'{paginate_parameters["sort_list"]}{paginate_parameters["time_field"]}{paginate_parameters["time_te"]}{cache_key}'
    doc_create(
        collection=get_collection('paginate_cache'),
        document={
            'name': cache_name,
            'key': cache_key,
            'value': cache_value
        },
    )
    return Paginate(
        items=cache_value[
            paginate_parameters['skip']:paginate_parameters['limit']],
        total=len(cache_value),
    )


# 服务启动时清理分页缓存数据
set_startup_task(lambda: get_collection('paginate_cache').delete_many({}))


def doc_create(collection: Collection, document: dict, **kw):
    """ 创建数据集合文档 """
    document['create_time'] = datetime.utcnow()
    document['update_time'] = datetime.utcnow()
    # 此步骤会自动为 user_json 添加 _id 信息
    collection.insert_one(document=document, **kw)


def doc_update(collection: Collection,
               filter: dict,
               update: dict,
               many: bool = False,
               **kw):
    """ 更新数据集合文档 """
    update['update_time'] = datetime.utcnow()
    if many:
        collection.update_many(filter=filter, update={'$set': update}, **kw)
    else:
        collection.update_one(filter=filter, update={'$set': update}, **kw)
