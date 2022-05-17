from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = 'We FastAPI'
    app_version: str = '0.0.1'
    app_host: str = 'http://127.0.0.1:8083/'
    app_workers_num: int = 1
    app_docs: bool = True
    app_redoc: bool = True
    token_expire_minute: int = 720
    token_secret_key: str = '2203a6a1be54a1ab3afad0e5ca16de1dfe2ee384f13fe4b710c0b16359db9983'
    mail_smtp_host: str = 'smtp.163.com'
    mail_smtp_use_ssl: bool = True
    mail_smtp_port: int = 465
    mail_smtp_sender: str = 'from@163.com'
    mail_smtp_password: str = 'xxxxxxx'
    wechat_app_id: str = ''
    wechat_app_secret: str = ''


settings_describe = {
    'app_name': '服务的标题',
    'app_version': '服务的版本号',
    'app_host': '服务的主机地址',
    'app_workers_num': '服务的工作进程数 (workers)',
    'app_docs': '服务的 Swagger 文档 <需重启>',
    'app_redoc': '服务的 ReDoc 文档 <需重启>',
    'token_expire_minute': '令牌的有效时间 (分钟) <需重启>',
    'token_secret_key': '令牌的密钥 (openssl rand -hex 32) <需重启>',
    'mail_smtp_host': '邮件 SMTP 服务器主机地址',
    'mail_smtp_use_ssl': '邮件 SMTP 服务器 SSL 加密',
    'mail_smtp_port': '邮件 SMTP 服务器主机端口',
    'mail_smtp_sender': '邮件 SMTP 服务器发件人邮箱',
    'mail_smtp_password': '邮件 SMTP 服务器授权码',
    'wechat_app_id': '[可选] 微信小程序唯一标识',
    'wechat_app_secret': '[可选] 微信小程序密钥',
}
