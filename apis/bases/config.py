from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = 'WeFastAPI'
    app_version: str = '0.0.1'
    app_host: str = 'http://127.0.0.1:8083/'
    app_home_path: str = '/view/bases/home/'
    app_home_path_anon: str = '/view/bases/home/'
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
    mail_smtp_port: int = 465
    mail_smtp_use_ssl: bool = True
    mail_smtp_sender_name: str = 'fromXX'
    mail_smtp_sender: str = 'from@163.com'
    mail_smtp_password: str = ''
    enable_ldap_ad: bool = False
    ldap_ad_host: str = '127.0.0.1'
    ldap_ad_bind_dn: str = 'Example\\zhangsan'
    ldap_ad_password: str = ''
    ldap_ad_search_base: str = 'OU=OU,DC=Example,DC=LOCAL'
    ldap_ad_search_filter: str = '(sAMAccountName={})'
    ldap_ad_email_suffix: str = '@example.com'


settings_describe = {
    'app_name': '服务的标题',
    'app_version': '服务的版本号',
    'app_host': '服务的地址',
    'app_home_path': '服务的主页路径 (已登录)',
    'app_home_path_anon': '服务的主页路径 (未登录)',
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
    'mail_smtp_host': '邮件 SMTP 服务器地址',
    'mail_smtp_port': '邮件 SMTP 服务器端口',
    'mail_smtp_use_ssl': '邮件 SMTP 使用 SSL 加密',
    'mail_smtp_sender_name': '邮件 SMTP 发件人名称',
    'mail_smtp_sender': '邮件 SMTP 发件人邮箱',
    'mail_smtp_password': '邮件 SMTP 授权码',
    'enable_ldap_ad': '启用 LDAP/AD 认证',
    'ldap_ad_host': 'LDAP/AD 服务器地址',
    'ldap_ad_bind_dn': 'LDAP/AD 绑定用户的 DN',
    'ldap_ad_password': 'LDAP/AD 绑定用户的密码',
    'ldap_ad_search_base': 'LDAP/AD 搜索用户的基础路径',
    'ldap_ad_search_filter': 'LDAP/AD 搜索用户的过滤器',
    'ldap_ad_email_suffix': 'LDAP/AD 企业邮箱后缀',
}
