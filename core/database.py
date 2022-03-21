from datetime import datetime
from pydantic import BaseModel
from core.logger import logger
from functools import lru_cache
from pymongo import MongoClient
from functools import lru_cache
from core.model import Paginate
from fastapi import HTTPException, status
from pymongo.collection import Collection
from core.dependencies import get_settings
from core.security import get_password_hash
from core.dynamic import set_role_permissions

# MongoDB 数据库客户端
DBClient = None


@lru_cache()
def get_collection(collection_name: str):
    ''' 获取 DB 集合 (同一参数仅创建一次) '''
    settings = get_settings()
    db = DBClient[settings.mongo_db_name]
    # 获取 pymongo.collection.Collection 实例
    collection = db[collection_name]
    return collection


def whether_to_initialize(apis_urls):
    ''' 判断数据库连接有效性 (首次连接时初始化) '''
    user_col = get_collection('user')
    role_col = get_collection('role')
    try:
        if not user_col.count_documents({}):
            role_result = role_col.find_one({'title': 'SuperAdministrator'})
            if not role_result:
                role_result = role_col.insert_one({
                    'title': 'SuperAdministrator',
                    'permissions': ['read_permission', 'read_role', 'create_role', 'delete_role', 'update_role', 'create_user', 'read_user_page', 'delete_user', 'update_user'],
                    'create_time': datetime.utcnow(),
                    'update_time': datetime.utcnow(),
                })
                role_id = str(role_result.inserted_id)
            else:
                role_id = str(role_result['_id'])
            user_col.insert_one({
                'username': 'admin',
                'email': 'admin@we.com',
                'full_name': 'Administrator',
                'disabled': False,
                'password': get_password_hash('123456'),
                'role_id': role_id,
                'create_time': datetime.utcnow(),
                'update_time': datetime.utcnow(),
            })
            logger.success(
                'For the first connection, initialize the administrator account: admin / 123456')
            logger.warning(
                'Please log in to the administrator account as soon as possible and change the password in time')
        set_role_permissions(role_col)
    except Exception as e:
        logger.error(f'Initializing MongoDB connection exception, {e}')


def create_db_client(apis_urls):
    ''' 创建 MongoDB 数据库客户端 '''
    settings = get_settings()
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
    ''' 关闭 MongoDB 数据库客户端 '''
    global DBClient
    DBClient.close()


@lru_cache()
def utc_offset():
    ''' UTC 时间与本地时间的差 '''
    local_time = datetime.fromtimestamp(0)
    utc_time = datetime.utcfromtimestamp(0)
    return local_time - utc_time


async def paginate_find(collection: Collection, paginate_parameters: dict, query_content: dict, item_model: BaseModel):
    ''' 分页查询 DB 集合中的数据 '''
    find_count = collection.count_documents(query_content)
    if not find_count:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='No matching data found',
        )
    if paginate_parameters['sort_list']:
        # 包括排序参数的查询
        find_results = collection.find(query_content).sort(
            key_or_list=paginate_parameters['sort_list'],
        ).skip(
            skip=paginate_parameters['skip'],
        ).limit(
            limit=paginate_parameters['limit'],
        )
    else:
        # 没有排序参数的查询
        find_results = collection.find(query_content).skip(
            skip=paginate_parameters['skip'],
        ).limit(
            limit=paginate_parameters['limit'],
        )
    items = []
    for result in find_results:
        # 将 UTC 时间转为本地时间
        result['create_time'] += utc_offset()
        result['update_time'] += utc_offset()
        # 使用指定的模型读取查询结果
        items.append(item_model(**result))
    return Paginate(items=items, total=find_count)


def doc_create(collection: Collection, document: dict, **kw):
    ''' 创建数据集合文档 '''
    document['create_time'] = datetime.utcnow()
    document['update_time'] = datetime.utcnow()
    # 此步骤会自动为 user_json 添加 _id 信息
    collection.insert_one(document=document, **kw)


def doc_update(collection: Collection, filter: dict, update: dict, many: bool = False, **kw):
    ''' 更新数据集合文档 '''
    update['update_time'] = datetime.utcnow()
    if many:
        collection.update_many(filter=filter, update={'$set': update}, **kw)
    else:
        collection.update_one(filter=filter, update={'$set': update}, **kw)
