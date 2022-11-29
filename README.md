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

变量读取的优先级排序:

1. 系统环境变量
2. `.env` 文件
3. 变量默认值

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

## 异步需求

### 轻量协程

如果一个异步任务需要进行数据读写、文件读写、数据状态短期追踪、发起第三方接口请求等耗时操作, 协程是一个很好的解决方案. 例如下面的 `coroutine_task_test` 函数, 通过协程执行某个异步任务:

```python
import asyncio

async def coroutine_task_test(name):
    """ 协程任务: 测试 """
    for i in range(5):
        await asyncio.sleep(60)  # 模拟任务执行内容
        return  # 一分钟后直接结束协程任务

@router.get('/')
async def read_test():
    # 创建一个协程任务
    asyncio.create_task(coroutine_task_test('参数name的值'))
    return {}
```

### 独立进程

如果一个异步任务需要调用其他语言编译的 SDK 时, 可以将这个任务写成一个脚本独立运行, 必要时可以多节点部署任务进程. 例如下面创建一个 `exec_tasks.py` 文件, 用于执行某个异步任务:

```python
import time
import random
import requests
import argparse
from pymongo import MongoClient

# 获取命令行参数
parser = argparse.ArgumentParser(description='ExecTasks')
parser.add_argument(
    '--service-host',
    dest='service_host',
    type=str,
    default='http://127.0.0.1:8083/',
    help='ServiceHost',
)
parser.add_argument(
    '--id',
    dest='id',
    type=int,
    default=0,
    help='ID',
)
args = parser.parse_args(
# 执行端编号
exec_id = f'ET-{args.id}'
# 数据库客户端及连接
db_client = MongoClient(host='127.0.0.1', port=27017)
db = db_client['test_database']

def service_request(method: str, path: str = 'api/', data=None, host: str = args.service_host, headers=None, is_repeat: bool = True, **kw):
    if headers is None:
        if method == 'GET':
            headers = {}
        else:
            headers = {'content-type': 'application/json'}
    if data is None:
        data = {}
    if '//' not in path:
        url = f'{host}{path}'
    else:
        url = path
    while True:
        err_str = ''
        res = None
        try:
            if method == 'POST':
                res = requests.post(url=url, json=data, headers=headers, **kw)
            elif method == 'DELETE':
                res = requests.delete(url=url, json=data, headers=headers, **kw)
            elif method == 'PUT':
                res = requests.put(url=url, json=data, headers=headers, **kw)
            else:
                res = requests.get(url=url, params=data, headers=headers, **kw)
            if res.status_code == 200:
                return res, err_str
            else:
                err_str = f'服务响应异常: {res.status_code} {res.reason} {res.text}'
        except requests.exceptions.ConnectTimeout:
            err_str = '服务请求异常: 连接超时或读取超时'
        except requests.exceptions.ConnectionError:
            err_str = '服务请求异常: 未知服务或网络异常'
        except Exception as err:
            err_str = f'服务请求异常: {err}'
        if is_repeat:
            print(err_str)
        else:
            return res, err_str
        time.sleep(60)

def log(level: str, message: str):
    """ 提交日志 level=debug|info|warning|error """
    print(f'[{level}] 执行端{exec_id}: {message}')
    service_request(method='POST', path='api/bases/logs/', data={'level': level, 'message': f'执行端{exec_id}: {message}'})

seconds = int(time.time())  # 获取基准时间戳
log('debug', '已启动')
while True:
    if int(time.time()) - seconds > random.randint(13, 23):
        try:
            time.sleep(360)  # 模拟任务执行内容
        except Exception as e:
            log('error', str(e))
        seconds = int(time.time())
```
