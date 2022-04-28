from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = 'We FastAPI'
    app_version: str = '0.0.1'
    app_host: str = 'http://127.0.0.1:8083/'
    # Token 密钥与过期分钟数
    token_expire_minute: int = 720
    token_secret_key: str = '2203a6a1be54a1ab3afad0e5ca16de1dfe2ee384f13fe4b710c0b16359db9983'
    # 允许跨域请求的源列表
    allow_origins: list = ["*"]
    # MongoDB 连接: 基本信息
    mongo_db_host: str = '127.0.0.1'
    mongo_db_port: int = 27017
    mongo_db_name: str = 'test_database'
    # MongoDB 连接: 认证信息
    mongo_db_username: str = ''
    mongo_db_password: str = ''
    # 用户未分配角色时的默认权限
    user_default_permission: list = []

    class Config:
        env_file = '.env'
