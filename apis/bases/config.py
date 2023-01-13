from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = 'WeFastAPI'
    app_version: str = '0.0.1'
    app_host: str = 'http://127.0.0.1:8083/'
    app_home_path: str = '/view/bases/home/'
    app_workers_num: int = 1
    app_docs: bool = True
    app_redoc: bool = True
    uvicorn_host: str = '0.0.0.0'
    uvicorn_port: int = 8083
    uvicorn_workers: int = 1
    uvicorn_reload: bool = False
    token_expire_minute: int = 720
    token_exempt_ip: list = []
    token_exempt_host: list = []
    mail_smtp_host: str = 'smtp.163.com'
    mail_smtp_use_ssl: bool = True
    mail_smtp_port: int = 465
    mail_smtp_sender_name: str = 'fromXX'
    mail_smtp_sender: str = 'from@163.com'
    mail_smtp_password: str = 'xxxxxxx'
    enable_ldap_ad: bool = False
    ldap_ad_label: str = 'LDAP'
    ldap_ad_host: str = 'ldap://127.0.0.1:389/'
    enable_wechat_app: bool = False
    wechat_app_id: str = ''
    wechat_app_secret: str = ''


settings_describe = {
    'app_name': '服务的标题',
    'app_version': '服务的版本号',
    'app_host': '服务的主机地址',
    'app_home_path': '服务的主页路径',
    'app_workers_num': '服务的工作进程总数 (workers)',
    'app_docs': '服务的 Swagger 文档 <需重启>',
    'app_redoc': '服务的 ReDoc 文档 <需重启>',
    'uvicorn_host': '单 Uvicorn 监听地址 <需重启>',
    'uvicorn_port': '单 Uvicorn 监听端口 <需重启>',
    'uvicorn_workers': '单 Uvicorn 工作进程 <需重启>',
    'uvicorn_reload': '单 Uvicorn 代码变更重新加载 <需重启>',
    'token_expire_minute': '令牌的有效时间 (分钟) <需重启>',
    'token_exempt_ip': '令牌豁免 IP 网络列表 (前面3段) <需重启>',
    'token_exempt_host': '令牌豁免 IP 主机列表 (完整4段) <需重启>',
    'mail_smtp_host': '邮件 SMTP 服务器主机地址',
    'mail_smtp_use_ssl': '邮件 SMTP 服务器 SSL 加密',
    'mail_smtp_port': '邮件 SMTP 服务器主机端口',
    'mail_smtp_sender_name': '邮件 SMTP 服务器发件人名称',
    'mail_smtp_sender': '邮件 SMTP 服务器发件人邮箱',
    'mail_smtp_password': '邮件 SMTP 服务器授权码',
    'enable_ldap_ad': '启用 LDAP/AD 认证',
    'ldap_ad_label': 'LDAP/AD 服务器人性化名称',
    'ldap_ad_host': 'LDAP/AD 服务器主机地址',
    'enable_wechat_app': '启用微信小程序支持',
    'wechat_app_id': '微信小程序唯一标识',
    'wechat_app_secret': '微信小程序密钥',
}
