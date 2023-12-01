# WeFastAPI 第一步

在 [we-fast-api](https://github.com/hekaiyou/we-fast-api) 项目下的 `apis` 目录中, 创建一个 `my_module` 目录:

```bash
my_module/
    __init__.py
    api_items.py
    routing.py
```

上面文件的代码内容和用途如下:

- **\_\_init\_\_.py** (模块识别文件)
   ```python
   # 空白文件
   ```
- **api_items.py** (模块接口文件)
   ```python
   from fastapi import APIRouter

   router = APIRouter(prefix='/items', )

   @router.get('/open/', summary='第一个接口 (开放)', )
   async def read_hello():
       return {'message': 'Hello World'}
   ```
- **routing.py** (模块路由文件)
   ```python
   from fastapi import APIRouter
   from . import api_items

   router = APIRouter(
       prefix='/my_module',
       tags=['my_module'],
   )

   router.include_router(api_items.router)
   ```

创建上面三个文件并复制代码, 运行 `python main.py` 启动后台服务:

```bash
$ python main.py
INFO:     Started server process [3452220]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8083
```

根据上面终端输出的服务地址, 打开浏览器访问 [http://127.0.0.1:8083/api/my_module/items/open/](http://127.0.0.1:8083/api/my_module/items/open/) 路径, 将看到如下的 JSON 响应:

```json
{"message": "Hello World"}
```

打开浏览器访问 [http://127.0.0.1:8083/docs/](http://127.0.0.1:8083/docs/) 路径, 将会看到 [Swagger UI](https://github.com/swagger-api/swagger-ui) API 文档。

打开浏览器访问 [http://127.0.0.1:8083/redoc/](http://127.0.0.1:8083/redoc/) 路径, 将会看到 [ReDoc](https://github.com/Rebilly/ReDoc) API 文档。

打开浏览器访问 [http://127.0.0.1:8083/](http://127.0.0.1:8083/) 路径, 将会看到 [we-fast-api](https://github.com/hekaiyou/we-fast-api) 框架的轻前端站点。

使用初始的管理员账户登录后进入主页, 这个轻前端站点是基于 [Pico.css](https://picocss.com/) 这个纯 CSS 框架搭建的。
