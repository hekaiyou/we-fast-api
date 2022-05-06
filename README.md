# We FastAPI

一个基于 [FastAPI](https://fastapi.tiangolo.com/) 的后端服务快速启动项目.

## 快速开始

创建 Python3 版本的虚拟环境:

```shell
$ python3 -m venv env
$ pip install -r requirements.txt
```

在根目录下创建一个配置环境变量的 `.env` 文件, 添加数据库的连接信息, 也可以选择直接配置系统环境变量:

```shell
MONGO_DB_HOST='127.0.0.1'
MONGO_DB_PORT=27017
MONGO_DB_NAME='test_database'
```

*根据数据库是否开启权限管理, 选择性使用 `MONGO_DB_USERNAME` 和 `MONGO_DB_PASSWORD` 环境变量配置数据库认证信息.*

使用指定的地址和端口启动项目:

```shell
$ uvicorn main:app --host 0.0.0.0 --port 8083 --reload
```

访问以下文档和服务地址:

- 通过 http://127.0.0.1:8083/ 打开基础 Web 站点.
- 通过 http://127.0.0.1:8083/api/ 访问对应的服务.
- 通过 http://127.0.0.1:8083/docs/ 打开由 [Swagger UI](https://github.com/swagger-api/swagger-ui) 提供的文档.
- 通过 http://127.0.0.1:8083/redoc/ 打开由 [ReDoc](https://github.com/Rebilly/ReDoc) 提供的文档.

### 微信小程序

在 `.env` 文件中添加微信小程序的的连接配置:

```shell
WECHAT_APP_ID='wxxxxxxxxxxxxxxxxx'
WECHAT_APP_SECRET='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
```

保存配置后微信小程序就可以调用 *GET /token/* 接口获取凭证.
