# We FastAPI

一个基于 [FastAPI](https://fastapi.tiangolo.com/) 的后端服务快速启动项目.

## 快速开始

创建 Python3 版本的虚拟环境:

```shell
$ python3 -m venv venv
$ source venv/bin/activate
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
$ python main.py
```

访问以下文档和服务地址:

- 通过 http://127.0.0.1:8083/ 打开基础 Web 站点.
- 通过 http://127.0.0.1:8083/api/ 访问对应的服务.
- 通过 http://127.0.0.1:8083/docs/ 打开由 [Swagger UI](https://github.com/swagger-api/swagger-ui) 提供的文档.
- 通过 http://127.0.0.1:8083/redoc/ 打开由 [ReDoc](https://github.com/Rebilly/ReDoc) 提供的文档.

### 微信小程序

访问 http://127.0.0.1:8083/view/bases/setup/update/particle-bases/ 地址打开 **更新 BASES 设置** 页面, 编辑 *Wechat app id* 和 *Wechat app secret* 输入框完成微信小程序配置, 就可以调用 `GET /api/bases/wechat/token/open/`*` 接口获取微信登录凭证.

## 部署

### 手动部署

以下操作在 Ubuntu 系统下进行, 首先配置环境变量.

```shell
$ sudo vim ~/.bashrc
export MONGO_DB_HOST=127.0.0.1
export MONGO_DB_PORT=27017
export MONGO_DB_NAME=test_database
$ source ~/.bashrc
```

创建自启动服务配置文件.

```shell
$ vim wefast.service
```

编辑自启动服务配置文件 `wefast.service` 的内容.

```shell
[Unit]
Description=WeFastAPI

[Service]
Type=simple
WorkingDirectory=/home/.../.../we-fast-api
ExecStart=/home/.../.../we-fast-api/env/bin/python main.py
Restart=on-failure
RestartSec=30s

[Install]
WantedBy=multi-user.target
```

*参数 `--workers` 指定的工作进程数需要同步在 **更新 BASES 设置** 页面编辑 "App workers num" 值.*

完成配置文件后, 就可以执行下列命令配置和管理服务:

- 注册服务: sudo systemctl enable /home/.../.../we-fast-api/wefast.service
- 启动服务: sudo systemctl start wefast
- 更新配置文件: sudo systemctl daemon-reload
- 重新启动服务: sudo systemctl restart wefast
- 查看服务启动状态: sudo service wefast status
- 查看服务日志: sudo journalctl -u wefast
- 清理10秒之前的日志: sudo journalctl --vacuum-time=10s
- 清理2小时之前的日志: sudo journactl --vacuum-time=2h
- 清理7天之前的日志: sudo journalctl --vacuum-time=7d

如果需要配置域名访问, 到 Nginx 配置目录下创建一个新配置.

```shell
cd /etc/nginx/conf.d
sudo touch xxxxxx.conf
sudo vim xxxxxx.conf
```

编辑以下内容以完成反向代理配置.

```shell
server {
    listen  80;
    server_name  xxxxxx.com;
    # 把 http 域名请求转成 https
    return  301  https://$host$request_uri;
}
server {
    listen  443  ssl;
    server_name  xxxxxx.com;
    access_log  /data/nginx-logs/wefast-access.log;
    error_log  /data/nginx-logs/wefast-error.log;
    # ssl  on;
    ssl_certificate  /.../.../xxxxxx.com.crt;
    ssl_certificate_key  /.../.../xxxxxx.com.key;
    client_body_buffer_size  256K;
    client_header_buffer_size  12k;
    client_max_body_size  100m;
    large_client_header_buffers  4  12k;
    location / {
        proxy_pass  http://127.0.0.1:8083;
        proxy_set_header  Host  $host;
        proxy_set_header  X-Real-IP  $remote_addr;
        proxy_set_header  X-Forwarded-For  $proxy_add_x_forwarded_for;
        proxy_set_header  X-Forwarded-Protocol  $scheme;
    }
}
```

完成域名配置后, 验证和更新 Nginx 服务:

- 验证配置是否正确: sudo nginx -t
- 更新配置并重启服务: sudo nginx -s reload
