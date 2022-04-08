# We FastAPI

一个基于 [FastAPI](https://fastapi.tiangolo.com/) 的后端服务快速启动项目.

## 快速开始

创建 Python3 版本的虚拟环境:

```shell
$ python3 -m venv env
$ pip install -r requirements.txt
```

在根目录下创建一个配置环境变量的 `.env` 文件, 添加数据库的连接信息:

```shell
MONGO_DB_USERNAME='admin'
MONGO_DB_PASSWORD='xxxxxx'
```

使用指定的地址和端口启动项目:

```shell
$ uvicorn main:app --host '0.0.0.0' --port 8083 --reload
```

访问以下文档和服务地址:

- 通过 http://127.0.0.1:8083/api 访问对应的服务.
- 通过 http://127.0.0.1:8083/docs 打开由 [Swagger UI](https://github.com/swagger-api/swagger-ui) 提供的文档.
- 通过 http://127.0.0.1:8083/redoc 打开由 [ReDoc](https://github.com/Rebilly/ReDoc) 提供的文档.

### 用户授权

访问 `http://127.0.0.1:8083/docs` 打开由 [Swagger UI](https://github.com/swagger-api/swagger-ui) 提供的文档.

1. 点击 **Authorize** 按钮打开登录窗口, 输入管理员账号密码并完成登录
2. 调用 *GET /api/users/user/* 接口获取用户数据列表
3. 调用 *GET /api/users/role/* 接口获取角色数据列表
4. 基于以上 **2** 和 **3** 步获取的数据调用 *PUT /api/users/user/{user_id}* 接口更新用户权限

### 微信小程序

在 `.env` 文件中添加微信小程序的的连接配置:

```shell
WECHAT_APP_ID='wxxxxxxxxxxxxxxxxx'
WECHAT_APP_SECRET='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
```

保存配置后微信小程序就可以调用 *GET /token/* 接口获取凭证.
