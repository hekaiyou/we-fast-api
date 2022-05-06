from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = 'We FastAPI'
    app_version: str = '0.0.1'
    app_host: str = 'http://127.0.0.1:8083/'
    token_expire_minute: int = 720
    token_secret_key: str = '2203a6a1be54a1ab3afad0e5ca16de1dfe2ee384f13fe4b710c0b16359db9983'
    wechat_app_id: str = ''
    wechat_app_secret: str = ''


settings_describe = {
    'app_name': '网站或服务的标题',
    'app_version': '网站或服务的版本号',
    'app_host': '网站或服务的主机地址',
    'token_expire_minute': '访问令牌的有效时间 (分钟)',
    'token_secret_key': '生产访问令牌的密钥 (openssl rand -hex 32)',
    'wechat_app_id': '[可选] 微信小程序唯一标识',
    'wechat_app_secret': '[可选] 微信小程序密钥',
}
