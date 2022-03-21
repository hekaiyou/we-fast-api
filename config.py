from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = 'We FastAPI'
    app_version: str = '0.0.1'
    # MongoDB 连接: 基本信息
    mongo_db_host: str = '127.0.0.1'
    mongo_db_port: int = 27017
    mongo_db_name: str = 'test_database'
    # MongoDB 连接: 认证信息
    mongo_db_username: str = ''
    mongo_db_password: str = ''

    class Config:
        env_file = '.env'
