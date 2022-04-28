from pydantic import BaseSettings


class Settings(BaseSettings):
    # 微信小程序配置
    wechat_app_id: str = ''
    wechat_app_secret: str = ''
