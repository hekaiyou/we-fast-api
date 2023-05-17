# We FastAPI

一个基于 [FastAPI](https://fastapi.tiangolo.com/) 的后端服务快速启动项目。

## 📦 安装

### 前置依赖

- 开发语言: Python >= 3.7
- 数据库: MongoDB >= 4.0

### 操作步骤

1. 下载 [we-fast-api](https://github.com/hekaiyou/we-fast-api) 框架代码并重命名为 `demo` 目录, 在终端执行:
   ```shell
   git clone https://github.com/hekaiyou/we-fast-api.git demo
   ```
2. 创建 Python3 版本的虚拟环境, 在终端执行:
   ```shell
   cd demo
   # 如果 python 找不到命令可以尝试 python3 命令
   python -m venv venv
   # Linux下执行
   source venv/bin/activate
   # Windows下执行
   # venv/Scripts/activate
   ```
3. 先安装 [we-fast-api](https://github.com/hekaiyou/we-fast-api) 框架依赖, 在终端执行:
   ```shell
   pip install -r requirements.txt
   ```

## ⚙️ 配置

环境变量读取的优先级排序, 有同名环境变量时, 取优先级高的变量值:

1. 系统环境变量
2. **.env** 文件 (用这个比较方便)
3. 环境变量默认值

| 应用模块 | 配置文件路径 | 描述 |
| ------- | ------- | ------- |
| core | `.env` | MongoDB 连接等关键配置 (应用运行不可缺少的环境变量) |
| bases | `apis/bases/.env` | [we-fast-api](https://github.com/hekaiyou/we-fast-api) 框架的基础环境变量 |

### .env

在框架根路径下创建 `.env` 配置文件, 参考以下内容设置具体的环境变量:

```bash
MONGO_DB_HOST=127.0.0.1
MONGO_DB_PORT=27017
MONGO_DB_NAME=demo
```

该目录下支持的全部环境变量参数如下:

| 环境变量 | 描述 | 类型 | 默认值 |
| ------- | ------- | ------- | ------- |
| MONGO_DB_HOST | MongoDB 连接地址 | str | 127.0.0.1 |
| MONGO_DB_PORT | MongoDB 连接端口 | int | 27017 |
| MONGO_DB_NAME | MongoDB 连接数据库 | str | test_database |
| MONGO_DB_USERNAME | MongoDB 连接认证用户 | str |  |
| MONGO_DB_PASSWORD | MongoDB 连接认证密码 | str |  |
| USER_DEFAULT_PERMISSION | 用户未分配角色时的默认权限 | list | [] |
| TOKEN_SECRET_KEY | 令牌的密钥 (生产建议使用 `openssl rand -hex 32` 生成新密钥) | str |  |

*根据数据库是否开启权限管理, 选择性使用 `MONGO_DB_USERNAME` 和 `MONGO_DB_PASSWORD` 变量配置数据库认证信息。*

### apis/bases/.env

在 `apis/bases/` 路径下创建 `.env` 配置文件, 参考以下内容设置具体的环境变量:

```bash
APP_NAME=Demo服务
APP_VERSION=1.0.0
APP_HOST=http://127.0.0.1:8083/
```

该目录下支持的全部环境变量参数如下:

| 环境变量 | 描述 | 类型 | 默认值 |
| ------- | ------- | ------- | ------- |
| APP_NAME | 服务的标题 | str | WeFastAPI |
| APP_VERSION | 服务的版本号, 通常按照 `A.B.C`(*大版本.新功能发布.小更新*) 规则 | str | 0.0.1 |
| APP_HOST | 服务的地址 | str | http://127.0.0.1:8083/ |
| APP_HOME_PATH | 服务的主页路径 (已登录) | str | /view/bases/home/ |
| APP_HOME_PATH_ANON | 服务的主页路径 (未登录) | str | /view/bases/home/ |
| APP_WORKERS_NUM | 服务的工作进程总数 (workers) | int | 1 |
| APP_DOCS | 服务的 Swagger 文档 (生产建议关闭) | bool | True |
| APP_REDOC | 服务的 ReDoc 文档 (生产建议关闭) | bool | True |
| UVICORN_HOST | 单 Uvicorn 监听地址 | str | 0.0.0.0 |
| UVICORN_PORT | 单 Uvicorn 监听端口 | int | 8083 |
| UVICORN_WORKERS | 单 Uvicorn 工作进程 | int | 1 |
| UVICORN_RELOAD | 单 Uvicorn 代码变更重新加载 | bool | False |
| TOKEN_EXPIRE_MINUTE | 令牌的有效时间 (分钟) | int | 720 |
| TOKEN_EXEMPT_IP | 令牌豁免 IP 网络列表 (前面3段) | list | [] |
| TOKEN_EXEMPT_HOST | 令牌豁免 IP 主机列表 (完整4段) | list | [] |
| MAIL_SMTP_HOST | 邮件 SMTP 服务器地址 | str | smtp.163.com |
| MAIL_SMTP_PORT | 邮件 SMTP 服务器端口 | int | 465 |
| MAIL_SMTP_USE_SSL | 邮件 SMTP 使用 SSL 加密 | bool | True |
| MAIL_SMTP_SENDER_NAME | 邮件 SMTP 发件人名称 | str | fromXX |
| MAIL_SMTP_SENDER | 邮件 SMTP 发件人邮箱 | str | from@163.com |
| MAIL_SMTP_PASSWORD | 邮件 SMTP 授权码 | str |  |
| ENABLE_LDAP_AD | 启用 LDAP/AD 认证 | bool | False |
| LDAP_AD_HOST | LDAP/AD 服务器地址 | str | 127.0.0.1 |
| LDAP_AD_BIND_DN | LDAP/AD 绑定用户的 DN | str | Example\\zhangsan |
| LDAP_AD_PASSWORD | LDAP/AD 绑定用户的密码 | str |  |
| LDAP_AD_SEARCH_BASE | LDAP/AD 搜索用户的基础路径 | str | OU=OU,DC=Example,DC=LOCAL |
| LDAP_AD_SEARCH_FILTER | LDAP/AD 搜索用户的过滤器 | str | (sAMAccountName={}) |
| LDAP_AD_EMAIL_SUFFIX | LDAP/AD 企业邮箱后缀 | str | @example.com |
| ENABLE_WECHAT_APP | 启用微信小程序支持 | bool | False |
| WECHAT_APP_ID | 微信小程序唯一标识 | str | wxa123456 |
| WECHAT_APP_SECRET | 微信小程序密钥 | str |  |

## ✨ 启动

在框架根路径下, 进入虚拟环境并执行:

```bash
# Linux下执行
source venv/bin/activate
# Windows下执行
# venv/Scripts/activate
python main.py
```

服务启动后, 可以访问以下文档和应用地址:

- 通过 http://127.0.0.1:8083/ 访问基础 Web 站点
- 通过 http://127.0.0.1:8083/docs/ 访问由 [Swagger UI](https://github.com/swagger-api/swagger-ui) API 文档
- 通过 http://127.0.0.1:8083/redoc/ 访问由 [ReDoc](https://github.com/Rebilly/ReDoc) API 文档

## 👀 预览

## 💨 部署

### Docker

框架中提供了一个基础的 `Dockerfile` 来构建镜像, 在框架根路径下创建 `Dockerfile` 文件:

```bash
FROM python:3.10.11
WORKDIR /workspace
COPY . /workspace/
RUN pip install -r requirements.txt
# Build serve - Start
# For example: RUN pip install -r apis/my_module/requirements.txt
# Build serve - End
EXPOSE 8083
CMD ["python", "main.py"]
```

使用这个 `Dockerfile` 来构建镜像:

```shell
docker build -t demo:1.0.0 .
```

先检查服务在镜像容器内是否正常运行:

```shell
docker run -t -i -v /{LOCAL_DIR}/files:/workspace/files -v /{LOCAL_DIR}/logs:/workspace/logs -p 8089:8083 --env-file .env --env-file apis/bases/.env demo:1.0.0
```

| 构建参数 | 作用描述 |
| ------- | ------- |
| -v /{LOCAL_DIR}/files:/workspace/files | 持久化的文件存储路径 |
| -v /{LOCAL_DIR}/logs:/workspace/logs | 持久化的日志存储路径 |
| --env-file .env | 从文件中读取 `core` 模块的环境变量 |
| --env-file apis/bases/.env | 从文件中读取 `bases` 模块的环境变量 |

确认服务正常后, 添加 `-d` 参数将容器放后台运行:

```shell
docker run -t -i -d -v /{LOCAL_DIR}/files:/workspace/files -v /{LOCAL_DIR}/logs:/workspace/logs -p 8089:8083 --env-file .env --env-file apis/bases/.env demo:1.0.0
```

*最后请确认框架根路径下的 `.env` 配置文件中, 已经使用 `openssl rand -hex 32` 生成新密钥, 并设置成环境变量 `TOKEN_SECRET_KEY` 的新值。*

### Linux

以下操作在 Ubuntu 系统下进行, 首先在框架根路径下创建自启动服务配置文件:

```shell
vim demo.service
```

编辑自启动服务配置文件 `demo.service` 的内容:

```shell
[Unit]
Description=demo

[Service]
Type=simple
WorkingDirectory=/{LOCAL_DIR}/demo
ExecStart=/{LOCAL_DIR}/demo/venv/bin/python main.py
Restart=on-failure
RestartSec=30s

[Install]
WantedBy=multi-user.target
```

完成配置文件后, 就可以执行下列命令配置和管理服务:

- 注册服务: sudo systemctl enable /{LOCAL_DIR}/demo/demo.service
- 启动服务: sudo systemctl start demo
- 更新配置文件: sudo systemctl daemon-reload
- 重新启动服务: sudo systemctl restart demo
- 查看服务启动状态: sudo service demo status
- 查看服务日志: sudo journalctl -u demo
- 清理10秒之前的日志: sudo journalctl --vacuum-time=10s
- 清理2小时之前的日志: sudo journactl --vacuum-time=2h
- 清理7天之前的日志: sudo journalctl --vacuum-time=7d

*此部署方式支持在 **参数设置** 菜单中动态变更环境变量。*
