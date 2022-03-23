from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = 'We FastAPI'
    app_version: str = '0.0.1'
    # 允许跨域请求的源列表
    allow_origins: list = ['*']
    # MongoDB 连接: 基本信息
    mongo_db_host: str = '127.0.0.1'
    mongo_db_port: int = 27017
    mongo_db_name: str = 'test_database'
    # MongoDB 连接: 认证信息
    mongo_db_username: str = ''
    mongo_db_password: str = ''
    # 用户未分配角色时的默认权限
    user_default_permission: list = []
    # 微信小程序配置
    weixin_app_id: str = ''
    weixin_app_secret: str = ''

    class Config:
        env_file = '.env'
